# Trial Visits (TV)

Visit-level mappings for encounter names, visit order, planned day logic, and visit rules.

## Variable Map

Open any row to view the full mapping details and notes on its details page.

<table class="sdtm-mapping-table">
<thead>
<tr>
<th>Variable</th>
<th>Label</th>
<th>USDM Class</th>
<th>USDM Path</th>
</tr>
</thead>
<tbody>
<tr class="sdtm-clickable-row" tabindex="0" role="link" onclick="window.location.href='../tv-details/001-studyid/index.html'" onkeydown="if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); window.location.href='../tv-details/001-studyid/index.html'; }">
<td><a class="sdtm-row-link" href="../tv-details/001-studyid/index.html"><code>STUDYID</code></a></td>
<td><a class="sdtm-row-link" href="../tv-details/001-studyid/index.html">Study Identifier</a></td>
<td><a class="sdtm-class-link" href="../../classes/StudyIdentifier/index.html" onclick="event.stopPropagation()">StudyIdentifier</a></td>
<td><a class="sdtm-row-link" href="../tv-details/001-studyid/index.html">StudyVersion/@studyIdentifiers/StudyIdentifier/@text</a></td>
</tr>
<tr class="sdtm-clickable-row" tabindex="0" role="link" onclick="window.location.href='../tv-details/002-domain/index.html'" onkeydown="if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); window.location.href='../tv-details/002-domain/index.html'; }">
<td><a class="sdtm-row-link" href="../tv-details/002-domain/index.html"><code>DOMAIN</code></a></td>
<td><a class="sdtm-row-link" href="../tv-details/002-domain/index.html">Domain Abbreviation</a></td>
<td></td>
<td></td>
</tr>
<tr class="sdtm-clickable-row" tabindex="0" role="link" onclick="window.location.href='../tv-details/003-visitnum/index.html'" onkeydown="if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); window.location.href='../tv-details/003-visitnum/index.html'; }">
<td><a class="sdtm-row-link" href="../tv-details/003-visitnum/index.html"><code>VISITNUM</code></a></td>
<td><a class="sdtm-row-link" href="../tv-details/003-visitnum/index.html">Visit Number</a></td>
<td><a class="sdtm-class-link" href="../../classes/Encounter/index.html" onclick="event.stopPropagation()">Encounter</a></td>
<td><a class="sdtm-row-link" href="../tv-details/003-visitnum/index.html">StudyVersion/@studyDesigns/StudyDesign/@encounters/Encounter/@next</a></td>
</tr>
<tr class="sdtm-clickable-row" tabindex="0" role="link" onclick="window.location.href='../tv-details/004-visit/index.html'" onkeydown="if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); window.location.href='../tv-details/004-visit/index.html'; }">
<td><a class="sdtm-row-link" href="../tv-details/004-visit/index.html"><code>VISIT</code></a></td>
<td><a class="sdtm-row-link" href="../tv-details/004-visit/index.html">Visit Name</a></td>
<td><a class="sdtm-class-link" href="../../classes/Encounter/index.html" onclick="event.stopPropagation()">Encounter</a></td>
<td><a class="sdtm-row-link" href="../tv-details/004-visit/index.html">StudyVersion/@studyDesigns/StudyDesign/@encounters/Encounter/@label</a></td>
</tr>
<tr class="sdtm-clickable-row" tabindex="0" role="link" onclick="window.location.href='../tv-details/005-visitdy/index.html'" onkeydown="if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); window.location.href='../tv-details/005-visitdy/index.html'; }">
<td><a class="sdtm-row-link" href="../tv-details/005-visitdy/index.html"><code>VISITDY</code></a></td>
<td><a class="sdtm-row-link" href="../tv-details/005-visitdy/index.html">Planned Study Day of Visit</a></td>
<td><a class="sdtm-class-link" href="../../classes/Timing/index.html" onclick="event.stopPropagation()">Timing</a></td>
<td><a class="sdtm-row-link" href="../tv-details/005-visitdy/index.html">StudyVersion/@studyDesigns/StudyDesign/@encounters /Encounter/@scheduledAt/Timing/@label</a></td>
</tr>
<tr class="sdtm-clickable-row" tabindex="0" role="link" onclick="window.location.href='../tv-details/006-armcd/index.html'" onkeydown="if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); window.location.href='../tv-details/006-armcd/index.html'; }">
<td><a class="sdtm-row-link" href="../tv-details/006-armcd/index.html"><code>ARMCD</code></a></td>
<td><a class="sdtm-row-link" href="../tv-details/006-armcd/index.html">Planned Arm Code</a></td>
<td><a class="sdtm-class-link" href="../../classes/StudyArm/index.html" onclick="event.stopPropagation()">StudyArm</a></td>
<td><a class="sdtm-row-link" href="../tv-details/006-armcd/index.html">StudyVersion/@studyDesigns/StudyDesign/@arms/StudyArm/@label</a></td>
</tr>
<tr class="sdtm-clickable-row" tabindex="0" role="link" onclick="window.location.href='../tv-details/007-arm/index.html'" onkeydown="if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); window.location.href='../tv-details/007-arm/index.html'; }">
<td><a class="sdtm-row-link" href="../tv-details/007-arm/index.html"><code>ARM</code></a></td>
<td><a class="sdtm-row-link" href="../tv-details/007-arm/index.html">Description of Planned Arm</a></td>
<td><a class="sdtm-class-link" href="../../classes/StudyArm/index.html" onclick="event.stopPropagation()">StudyArm</a></td>
<td><a class="sdtm-row-link" href="../tv-details/007-arm/index.html">StudyVersion/@studyDesigns/StudyDesign/@arms/StudyArm/@description</a></td>
</tr>
<tr class="sdtm-clickable-row" tabindex="0" role="link" onclick="window.location.href='../tv-details/008-tvenrl/index.html'" onkeydown="if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); window.location.href='../tv-details/008-tvenrl/index.html'; }">
<td><a class="sdtm-row-link" href="../tv-details/008-tvenrl/index.html"><code>TVENRL</code></a></td>
<td><a class="sdtm-row-link" href="../tv-details/008-tvenrl/index.html">Visit End Rule</a></td>
<td><a class="sdtm-class-link" href="../../classes/TransitionRule/index.html" onclick="event.stopPropagation()">TransitionRule</a></td>
<td><a class="sdtm-row-link" href="../tv-details/008-tvenrl/index.html">StudyVersion/@studyDesigns/StudyDesign/@encounters /Encounter/@transitionEndRule /TransitionRule/@text</a></td>
</tr>
<tr class="sdtm-clickable-row" tabindex="0" role="link" onclick="window.location.href='../tv-details/009-tvstrl/index.html'" onkeydown="if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); window.location.href='../tv-details/009-tvstrl/index.html'; }">
<td><a class="sdtm-row-link" href="../tv-details/009-tvstrl/index.html"><code>TVSTRL</code></a></td>
<td><a class="sdtm-row-link" href="../tv-details/009-tvstrl/index.html">Visit Start Rule</a></td>
<td><a class="sdtm-class-link" href="../../classes/TransitionRule/index.html" onclick="event.stopPropagation()">TransitionRule</a></td>
<td><a class="sdtm-row-link" href="../tv-details/009-tvstrl/index.html">StudyVersion/@studyDesigns/StudyDesign/@encounters/Encounter/@transitionStartRule/TransitionRule/@text</a></td>
</tr>
</tbody>
</table>
