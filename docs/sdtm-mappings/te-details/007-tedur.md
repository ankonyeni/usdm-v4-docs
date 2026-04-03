# TE.TEDUR

<div class="sdtm-detail-card">
  <p class="sdtm-detail-meta"><strong>Label:</strong> Planned Duration of Element</p>
  <p class="sdtm-detail-meta"><strong>USDM Class:</strong> <a href="../../../classes/Timing/">Timing</a></p>
  <p class="sdtm-detail-meta"><strong>USDM Path:</strong> <code>StudyVersion/@studyDesigns/StudyDesign/@scheduleTimelines/ScheduleTimeline/@timings/Timing/@value</code></p>
</div>

## Mapping Details

<div class="sdtm-rule-list"><p><strong>Target Notes:</strong> The element length can be calculated based on timing values based on the used logic for a trial. For example select the last timing value of epoch related to the element and subtract the timing value of the last scheduledInstance referencing to the previous epoch.</p><p><strong>Condition Path:</strong> <code>StudyVersion/@studyDesigns/StudyDesign/@elements/StudyElement/@id=StudyVersion/@studyDesigns/StudyDesign/@studyCells/StudyCell/@elements | StudyVersion/@studyDesigns/StudyDesign/@studyCells/StudyCell/@epoch = StudyVersion/@studyDesigns/StudyDesign/@scheduleTimelines/ScheduleTimeline/@instances/ScheduledActivityInstance/@epoch</code></p></div>
