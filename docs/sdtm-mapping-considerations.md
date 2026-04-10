# General Considerations

This page summarizes cross-cutting considerations for the SDTM trial design mapping pages across TA, TE, TI, and TV.

The content reflects repository-specific implementation suggestions and is not official CDISC guidance.

## Optional USDM Source Slots

Some SDTM mappings rely on USDM fields such as [`label`](slots/label.md) or [`description`](slots/description.md). These fields can be useful mapping sources, but they are optional in the model.

If a mapping depends on an optional slot and that slot is not populated, the SDTM variable may be missing or require special-case fallback logic. This creates avoidable variability across studies and implementations.

When an optional slot is important for SDTM generation, one possible approach is to treat it as operationally required within local authoring and validation rules. In practice, that could include:

- defining expectations for which optional fields are expected to be populated to support SDTM generation;
- validating those fields before deriving SDTM outputs; and
- documenting fallback behavior if a mapping source is unavailable.

## SDTM Variable Constraints

Several SDTM variables impose restrictions on value length, character set, or formatting. These constraints are worth considering early because descriptive USDM source values may not always be directly usable as SDTM outputs.

### Common constraints

- Character variables are generally limited to 200 characters.
- `--TESTCD` values must be no more than 8 characters, cannot begin with a number, and may contain only letters, numbers, or underscores.
- `ETCD` and `TSPARMCD` are limited to 8 characters.
- `ARMCD` is limited to 20 characters.

Common approaches include:

1. Author SDTM-compatible values directly in the USDM source field.
2. Apply a controlled post-processing step that converts the source value into an SDTM-compliant representation.

Where transformation is introduced, it can be helpful for the logic to be deterministic, documented, and traceable back to the original USDM value.

## Long Eligibility Criterion Text

This consideration is most directly relevant to [`TI.IETEST`](sdtm-mappings/ti-details/004-ietest.md). Eligibility criterion text can easily exceed the 200-character limit generally used for SDTM character variables, especially when mapping criterion wording intended for human readability into concise SDTM values.

If criterion text exceeds 200 characters, it should be summarized to fit within that limit while preserving meaning. Truncation should be used only as a last resort.

## Data Type Mismatches and Structured Values

Some mappings require an SDTM variable of one data type to be derived from a USDM field of a different type. A common example is [`TV.VISITDY`](sdtm-mappings/tv-details/005-visitdy.md), which is numeric in SDTM but may be derived from a character-based USDM value.

When a numeric SDTM value is derived from free text or a character label, the mapping depends on conventions that may not be explicit in the data model. This increases transformation complexity and the risk of inconsistent implementation.

A structured source that directly represents the intended numeric value may be easier to maintain than deriving the value from free text. If a character-based field is used, it may help to constrain its content so that the value can be converted reliably and unambiguously.

## Epoch Mapping for [`TA.EPOCH`](sdtm-mappings/ta-details/010-epoch.md)

The current mapping for [`TA.EPOCH`](sdtm-mappings/ta-details/010-epoch.md) uses `StudyVersion/@studyDesigns/StudyDesign/@epochs/StudyEpoch/@label`. While this is a workable source in some implementations, it has two important limitations:

- [`label`](slots/label.md) is optional; and
- `EPOCH` is associated with controlled terminology, so a free-text label may require remapping before it is suitable for SDTM.

It may be worth evaluating whether [`StudyEpoch.type`](classes/StudyEpoch.md) offers a more robust source for [`TA.EPOCH`](sdtm-mappings/ta-details/010-epoch.md), because:

- it is required;
- it uses the [`Code`](classes/Code.md) data type, which is more naturally aligned with terminology-based mapping.

If [`label`](slots/label.md) remains the mapping source, a terminology normalization step may also be useful so that the derived `EPOCH` value is more consistent with SDTM expectations.

## Using the USDM Extension Mechanism

Some SDTM requirements may not be represented cleanly using only the base USDM slots. In these cases, the USDM extension mechanism can be used to capture additional structured information needed for downstream processing.

It may also be helpful to keep in mind that USDM is not intended solely for mapping SDTM trial domains. Because USDM supports broader study definition use cases, it may not always be desirable to change the wording, structure, or formatting of core USDM slots only to make a particular SDTM mapping easier. In that kind of situation, the extension mechanism can offer a way to preserve the broader intent of the base USDM content while still carrying implementation-specific values that support SDTM derivation.

From an implementation perspective, it may also help to remember that the extension mechanism is exposed through the API rather than through the core logical model itself. In practice, this means a class can carry an [`extensionAttributes`](slots/extensionAttributes.md) collection made up of [`ExtensionAttribute`](classes/ExtensionAttribute.md) entries. Each entry can be thought of as a small extension container that identifies the extension through its own identifier and URL, and then carries the extension value. Depending on the use case, that value may be represented as a simple datatype, a more complex datatype, or by using one or more [`ExtensionClass`](classes/ExtensionClass.md) instances. For clarity and ease of processing, the pattern is easiest to work with when each [`ExtensionAttribute`](classes/ExtensionAttribute.md) instance expresses a single extension value. The URL also helps make the extension uniquely identifiable, while separate implementation documentation can describe how a given extension is intended to be used.

### When extensions are useful

Extensions can be especially helpful when:

- the source field is descriptive text but the SDTM output needs a coded or numeric value;
- the source field is human-readable but not transformation-safe; or
- the implementation must retain both an author-friendly value and an SDTM-ready value.

### Example

Instead of deriving [`TV.VISITDY`](sdtm-mappings/tv-details/005-visitdy.md) from a [`label`](slots/label.md) such as `SD7`, an implementation could store the planned study day explicitly in an extension attribute:

```yaml
id: Timing_3
name: TIM3
label: SD7
type:
  id: Code_39
  code: C201356
  codeSystem: ncit
  codeSystemVersion: 24.04e
  decode: After
relativeToFrom:
  id: Code_32
  code: C201355
  codeSystem: ncit
  codeSystemVersion: 24.04e
  decode: Start to Start
value: P3D
valueLabel: 3 days
relativeToScheduledInstanceId: ScheduledActivityInstance_3
extensionAttributes:
  - id: ext-study-day
    url: https://example.org/usdm/extensions/study-day
    valueInteger: 7
```

This approach makes the intended numeric mapping explicit and reduces reliance on parsing conventions.

## External Proof of Concept

Users who want to see one practical example of SDTM trial design mapping from USDM can look at Anthony Chow's [USDM to TDM Converter](https://github.com/chowsanthony/usdm2tdm). It is an external proof of concept that converts USDM JSON into SDTM trial design datasets using JSONata expressions.

The repository can be useful to review or try out if you want to see how TA, TE, TI, and TV-style mappings can be derived from USDM in code. Its README notes that it was developed with USDM v3 guidance, so it is best viewed as an illustrative example rather than a reference implementation for this site.

## Possible Implementation Practices

Possible practices that may improve the quality and consistency of SDTM trial design mappings include:

- identify which optional USDM fields are required in practice for SDTM generation;
- establish documented transformation rules for code shortening, terminology normalization, and text reduction;
- validate source values before SDTM derivation begins;
- prefer structured or coded source fields over free-text fields when both are available; and
- use extensions deliberately when the model does not provide a suitable mapping source.
