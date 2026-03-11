from __future__ import annotations

import copy
import re
from pathlib import Path
from typing import Any

import yaml

DEFAULT_MAPPING = Path("mappings/usdm_v4.mapping.yaml")


class ImporterError(ValueError):
    pass


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
    if not isinstance(data, dict):
        raise ImporterError(f"Expected a mapping at {path}, got {type(data).__name__}.")
    return data


def _dump_yaml(data: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        yaml.safe_dump(data, stream, sort_keys=False, allow_unicode=False)


def _is_scalar(value: Any) -> bool:
    return isinstance(value, (str, int, float, bool))


class DdfRaToLinkmlImporter:
    def __init__(self, source_model: dict[str, Any], mapping: dict[str, Any]) -> None:
        self.source_model = source_model
        self.mapping = mapping
        self.class_names = set(source_model)
        self.source_model_config = mapping["source_model"]
        self.defaults = mapping["defaults"]
        self.emission = mapping["emission"]
        self.overrides = mapping.get("overrides", {})

    def convert(self) -> dict[str, Any]:
        schema = copy.deepcopy(self.mapping["target"]["schema"])

        if self.emission.get("include_schema_annotations"):
            schema["annotations"] = self._merge_annotations(
                schema.get("annotations"),
                self._stringify_mapping(self.emission.get("schema_annotations", {})),
            )

        classes: dict[str, Any] = {}
        for class_name, class_definition in self.source_model.items():
            if not isinstance(class_definition, dict):
                raise ImporterError(f"Class '{class_name}' is not a mapping.")
            classes[class_name] = self._convert_class(class_name, class_definition)

        schema["classes"] = classes
        return schema

    def _convert_class(self, class_name: str, class_definition: dict[str, Any]) -> dict[str, Any]:
        class_fields = self.source_model_config["class_fields"]
        class_defaults = self.defaults["classes"]
        class_override = self.overrides.get("classes", {}).get(class_name, {})

        linkml_class: dict[str, Any] = {}

        title = self._get_scalar(class_definition, class_fields.get("title"))
        if title:
            linkml_class["title"] = title

        description = self._get_scalar(class_definition, class_fields.get("description"))
        if description:
            linkml_class["description"] = description

        modifier = self._get_scalar(class_definition, class_fields.get("modifier"))
        modifier_map = class_defaults.get("modifier_to_abstract", {})
        if modifier in modifier_map:
            abstract_value = modifier_map[modifier]
        else:
            abstract_value = class_defaults.get("if_modifier_missing", {}).get("abstract", False)

        if abstract_value or class_defaults.get("emit_abstract_false", True):
            linkml_class["abstract"] = abstract_value

        class_uri_pattern = class_defaults.get("class_uri_pattern")
        if class_uri_pattern:
            linkml_class["class_uri"] = class_uri_pattern.format(class_name=class_name)

        class_is_a = self._resolve_class_is_a(class_name, class_definition)
        if class_is_a:
            linkml_class["is_a"] = class_is_a

        exact_mappings = self._resolve_exact_mappings(class_definition)
        if exact_mappings:
            linkml_class["exact_mappings"] = exact_mappings

        if self.emission.get("include_class_annotations"):
            annotations = self._build_annotations(
                class_definition, class_fields.get("annotations", {})
            )
            if annotations:
                linkml_class["annotations"] = annotations

        if class_name == self.source_model_config.get("root_class"):
            linkml_class["tree_root"] = True
        if class_override.get("tree_root") is True:
            linkml_class["tree_root"] = True

        attributes = self._convert_attributes(class_name, class_definition, class_is_a)
        if attributes:
            linkml_class["attributes"] = attributes

        return linkml_class

    def _convert_attributes(
        self, class_name: str, class_definition: dict[str, Any], class_is_a: str | None
    ) -> dict[str, Any]:
        slot_container_key = self.source_model_config["class_fields"]["slots"]
        source_attributes = class_definition.get(slot_container_key) or {}
        if not isinstance(source_attributes, dict):
            raise ImporterError(
                f"Expected '{slot_container_key}' on class '{class_name}' to be a mapping."
            )

        attributes: dict[str, Any] = {}
        for slot_name, slot_definition in source_attributes.items():
            if not isinstance(slot_definition, dict):
                raise ImporterError(
                    f"Slot '{class_name}.{slot_name}' is not a mapping in the source model."
                )
            if self._slot_is_ignored(slot_name):
                continue
            if self._slot_is_inherited_from_parent(class_name, class_is_a, slot_name, slot_definition):
                continue
            emitted_slot_name = self._resolve_slot_name(slot_name, slot_definition)
            if emitted_slot_name in attributes:
                raise ImporterError(
                    f"Duplicate emitted slot name '{emitted_slot_name}' in class '{class_name}'."
                )
            attributes[emitted_slot_name] = self._convert_slot(
                class_name, slot_name, slot_definition
            )
        return attributes

    def _convert_slot(
        self, class_name: str, slot_name: str, slot_definition: dict[str, Any]
    ) -> dict[str, Any]:
        slot_fields = self.source_model_config["slot_fields"]
        slot_defaults = self.defaults["slots"]

        linkml_slot: dict[str, Any] = {}

        title = self._get_scalar(slot_definition, slot_fields.get("title"))
        if title:
            linkml_slot["title"] = title

        description = self._get_scalar(slot_definition, slot_fields.get("description"))
        if description:
            linkml_slot["description"] = description

        type_information = self._resolve_type(slot_name, slot_definition)
        if "range" in type_information:
            linkml_slot["range"] = type_information["range"]
        if "any_of" in type_information:
            linkml_slot["any_of"] = type_information["any_of"]

        cardinality = self._resolve_cardinality(class_name, slot_name, slot_definition)
        linkml_slot.update(cardinality)

        if slot_name in slot_defaults.get("identifier_slot_names", []):
            linkml_slot["identifier"] = True

        inlined = self._resolve_inlined(slot_definition, type_information["kinds"])
        if inlined is not None:
            linkml_slot["inlined"] = inlined

        exact_mappings = self._resolve_exact_mappings(slot_definition)
        if exact_mappings:
            linkml_slot["exact_mappings"] = exact_mappings

        if self.emission.get("include_slot_annotations"):
            annotations = self._build_annotations(slot_definition, slot_fields.get("annotations", {}))
            if annotations:
                linkml_slot["annotations"] = annotations

        return linkml_slot

    def _slot_is_ignored(self, slot_name: str) -> bool:
        slot_override = self.overrides.get("slots", {}).get(slot_name, {})
        return slot_override.get("ignore", False) is True

    def _resolve_slot_name(self, source_slot_name: str, slot_definition: dict[str, Any]) -> str:
        naming = self.defaults["naming"]
        if naming.get("preserve_slot_names", True):
            return source_slot_name

        source_field = naming.get("slot_name_source")
        if source_field:
            candidate = self._get_scalar(slot_definition, source_field)
            if candidate:
                return candidate

        fallback = naming.get("slot_name_fallback", "source_key")
        if fallback == "source_key":
            return source_slot_name

        raise ImporterError(
            f"Unable to resolve emitted slot name for source slot '{source_slot_name}'."
        )

    def _slot_is_inherited_from_parent(
        self,
        class_name: str,
        class_is_a: str | None,
        slot_name: str,
        slot_definition: dict[str, Any],
    ) -> bool:
        if not class_is_a:
            return False

        inherited_slots = self.defaults.get("inherited_slots")
        if not inherited_slots or not inherited_slots.get("omit_when_class_is_a"):
            return False

        source_field = self.source_model_config["slot_fields"].get("inherited_from")
        source_field = source_field or inherited_slots.get("source_field")
        inherited_refs = slot_definition.get(source_field)
        if inherited_refs is None:
            return False

        self._resolve_symbol_refs(
            item_name=f"{class_name}.{slot_name}",
            refs=inherited_refs,
            ref_key=inherited_slots["ref_key"],
            ref_prefix=inherited_slots["ref_prefix"],
            strip_prefix=inherited_slots.get("strip_prefix", True),
            ref_list_policy=inherited_slots["ref_list_policy"],
            validate_target_exists_in_source=inherited_slots.get(
                "validate_target_exists_in_source", True
            ),
            on_unknown_ref=inherited_slots.get("on_unknown_ref", "error"),
        )
        return True

    def _resolve_cardinality(
        self, class_name: str, slot_name: str, slot_definition: dict[str, Any]
    ) -> dict[str, Any]:
        slot_fields = self.source_model_config["slot_fields"]
        cardinality_value = self._get_scalar(slot_definition, slot_fields.get("cardinality"))
        cardinality_map = self.defaults["cardinality_map"]
        if cardinality_value not in cardinality_map:
            parsed_cardinality = self._parse_cardinality(cardinality_value)
            if parsed_cardinality is None:
                raise ImporterError(
                    f"Unsupported cardinality '{cardinality_value}' for '{class_name}.{slot_name}'."
                )
            return parsed_cardinality
        return copy.deepcopy(cardinality_map[cardinality_value])

    @staticmethod
    def _parse_cardinality(cardinality_value: str | None) -> dict[str, Any] | None:
        if not cardinality_value:
            return None
        match = re.fullmatch(r"(\d+)\.\.(\d+|\*)", cardinality_value)
        if not match:
            return None

        lower = int(match.group(1))
        upper = match.group(2)
        resolved: dict[str, Any] = {"required": lower > 0}
        if upper != "1":
            resolved["multivalued"] = True
        if lower not in (0, 1):
            resolved["minimum_cardinality"] = lower
        if upper not in ("*", "1"):
            resolved["maximum_cardinality"] = int(upper)
        return resolved

    def _resolve_type(self, slot_name: str, slot_definition: dict[str, Any]) -> dict[str, Any]:
        slot_fields = self.source_model_config["slot_fields"]
        type_entries = slot_definition.get(slot_fields["type"])
        if not isinstance(type_entries, list) or not type_entries:
            raise ImporterError(f"Slot '{slot_name}' has no usable Type list.")

        policy = self.defaults["ref_resolution"]["type_list_policy"]
        resolved_entries = [self._resolve_ref(slot_name, entry) for entry in type_entries]
        kinds = [entry["kind"] for entry in resolved_entries]

        if len(resolved_entries) == 1:
            return {"range": resolved_entries[0]["range"], "kinds": kinds}

        if policy != "union_any_of":
            raise ImporterError(
                f"Slot '{slot_name}' has {len(resolved_entries)} types but policy is '{policy}'."
            )

        return {
            "any_of": [{"range": entry["range"]} for entry in resolved_entries],
            "kinds": kinds,
        }

    def _resolve_ref(self, slot_name: str, entry: Any) -> dict[str, str]:
        ref_config = self.defaults["ref_resolution"]
        ref_key = self.source_model_config["slot_fields"]["ref_key"]

        if not isinstance(entry, dict) or ref_key not in entry:
            raise ImporterError(
                f"Slot '{slot_name}' has a Type entry without '{ref_key}': {entry!r}."
            )

        ref_value = entry[ref_key]
        ref_override = ref_config.get("overrides", {}).get(ref_value)
        if ref_override:
            return {
                "kind": ref_override["kind"],
                "range": ref_override["range"],
            }

        primitive_ref = ref_config["primitive_refs"].get(ref_value)
        if primitive_ref:
            return {"kind": primitive_ref["kind"], "range": primitive_ref["range"]}

        class_ref_config = ref_config["class_refs"]
        prefix = class_ref_config["prefix"]
        if ref_value.startswith(prefix):
            range_name = ref_value[len(prefix) :] if class_ref_config.get("strip_prefix") else ref_value
            if class_ref_config.get("validate_target_exists_in_source") and range_name not in self.class_names:
                raise ImporterError(
                    f"Slot '{slot_name}' references unknown class '{range_name}' via '{ref_value}'."
                )
            return {"kind": class_ref_config["kind"], "range": range_name}

        if ref_config.get("on_unknown_ref") == "error":
            raise ImporterError(f"Slot '{slot_name}' has unknown ref '{ref_value}'.")

        return {"kind": "scalar", "range": "string"}

    def _resolve_class_is_a(
        self, item_name: str, source_definition: dict[str, Any]
    ) -> str | None:
        inheritance = self.defaults["inheritance"]
        source_field = self.source_model_config["class_fields"].get("is_a")
        source_field = source_field or inheritance["source_field"]
        refs = source_definition.get(source_field)
        if refs is None:
            return None
        resolved = self._resolve_symbol_refs(
            item_name=item_name,
            refs=refs,
            ref_key=inheritance["ref_key"],
            ref_prefix=inheritance["ref_prefix"],
            strip_prefix=inheritance.get("strip_prefix", True),
            ref_list_policy=inheritance["ref_list_policy"],
            validate_target_exists_in_source=inheritance.get(
                "validate_target_exists_in_source", True
            ),
            on_unknown_ref=inheritance.get("on_unknown_ref", "error"),
        )
        return resolved[0] if resolved else None

    def _resolve_symbol_refs(
        self,
        item_name: str,
        refs: Any,
        ref_key: str,
        ref_prefix: str,
        strip_prefix: bool,
        ref_list_policy: str,
        validate_target_exists_in_source: bool,
        on_unknown_ref: str,
    ) -> list[str]:
        if not isinstance(refs, list) or not refs:
            raise ImporterError(f"'{item_name}' has an empty or invalid ref list.")

        if ref_list_policy == "single_ref_required" and len(refs) != 1:
            raise ImporterError(
                f"'{item_name}' has {len(refs)} refs but policy is '{ref_list_policy}'."
            )

        resolved: list[str] = []
        for ref_entry in refs:
            if not isinstance(ref_entry, dict) or ref_key not in ref_entry:
                raise ImporterError(f"'{item_name}' has an invalid ref entry: {ref_entry!r}.")

            ref_value = ref_entry[ref_key]
            if not isinstance(ref_value, str) or not ref_value.startswith(ref_prefix):
                if on_unknown_ref == "error":
                    raise ImporterError(
                        f"'{item_name}' ref '{ref_value}' does not start with '{ref_prefix}'."
                    )
                continue

            range_name = ref_value[len(ref_prefix) :] if strip_prefix else ref_value
            if validate_target_exists_in_source and range_name not in self.class_names:
                raise ImporterError(f"'{item_name}' references unknown class '{range_name}'.")
            resolved.append(range_name)

        return resolved

    def _resolve_inlined(self, slot_definition: dict[str, Any], resolved_kinds: list[str]) -> bool | None:
        inline_config = self.defaults["slots"]["relationship_type_inline"]
        relationship_value = self._get_scalar(slot_definition, inline_config["source_field"])
        if not relationship_value:
            return None if inline_config.get("on_missing") == "omit" else False

        if "class" not in resolved_kinds:
            return None

        inline_map = inline_config["map"]
        if relationship_value not in inline_map:
            if inline_config.get("on_unknown_value") == "error":
                raise ImporterError(f"Unknown Relationship Type '{relationship_value}'.")
            return None
        return inline_map[relationship_value]

    def _resolve_exact_mappings(self, source_definition: dict[str, Any]) -> list[str]:
        config = self.defaults["exact_mappings"]
        if not config.get("enabled"):
            return []

        source_value = self._get_scalar(source_definition, config["source_field"])
        if not source_value:
            return [] if config.get("on_missing") == "omit" else []

        pattern = config.get("value_pattern")
        if pattern and not re.fullmatch(pattern, source_value):
            if config.get("on_invalid_value") == "error":
                raise ImporterError(f"Invalid exact mapping value '{source_value}'.")
            return []

        return [config["curie_template"].format(value=source_value)]

    def _build_annotations(
        self, source_definition: dict[str, Any], annotations_map: dict[str, str]
    ) -> dict[str, str]:
        annotations: dict[str, str] = {}
        for target_name, source_name in annotations_map.items():
            value = source_definition.get(source_name)
            if value is None:
                continue
            if _is_scalar(value):
                annotations[target_name] = str(value)
        return annotations

    @staticmethod
    def _stringify_mapping(values: dict[str, Any]) -> dict[str, str]:
        result: dict[str, str] = {}
        for key, value in values.items():
            if _is_scalar(value):
                result[key] = str(value)
        return result

    @staticmethod
    def _merge_annotations(
        original: dict[str, Any] | None, new_values: dict[str, str]
    ) -> dict[str, str]:
        merged: dict[str, str] = {}
        if isinstance(original, dict):
            for key, value in original.items():
                if _is_scalar(value):
                    merged[key] = str(value)
        merged.update(new_values)
        return merged

    @staticmethod
    def _get_scalar(source_definition: dict[str, Any], source_field: str | None) -> str | None:
        if not source_field:
            return None
        value = source_definition.get(source_field)
        if value is None:
            return None
        if not _is_scalar(value):
            raise ImporterError(
                f"Expected scalar value for '{source_field}', got {type(value).__name__}."
            )
        return str(value)


def convert_ddf_ra_to_linkml(
    source: Path,
    output: Path,
    mapping_path: Path = DEFAULT_MAPPING,
) -> dict[str, Any]:
    mapping = _load_yaml(mapping_path)
    source_model = _load_yaml(source)
    importer = DdfRaToLinkmlImporter(source_model=source_model, mapping=mapping)
    schema = importer.convert()
    _dump_yaml(schema, output)
    return schema
