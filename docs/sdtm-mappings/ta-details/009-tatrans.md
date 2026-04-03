# TA.TATRANS

<div class="sdtm-detail-card">
  <p class="sdtm-detail-meta"><strong>Label:</strong> Transition Rule</p>
  <p class="sdtm-detail-meta"><strong>USDM Class:</strong> <a href="../../classes/ConditionAssignment/index.html">ConditionAssignment</a></p>
  <p class="sdtm-detail-meta"><strong>USDM Path:</strong> <code>StudyVersion/@studyDesigns/StudyDesign/@scheduleTimelines/ScheduleTimeline/@instances/ScheduledDecisionInstance/@conditionAssignments/ConditionAssignment/@condition</code></p>
</div>

## Mapping Details

<div class="sdtm-rule-list"><p><strong>Condition Notes:</strong> If the condition points to an scheduledActivityInstance which refers to the same epoch then the transition rule can be disregarded for SDTM TATRANS variable creation.</p><p><strong>Condition Path:</strong> <code>StudyVersion/@studyDesigns/StudyDesign/@arms/StudyArm/@id=StudyVersion/@studyDesigns/StudyDesign/@studyCells/StudyCell/@arm | StudyVersion/@studyDesigns/StudyDesign/@elements/StudyElement/@id=StudyVersion/@studyDesigns/StudyDesign/@studyCells/StudyCell/@elements | StudyVersion/@studyDesigns/StudyDesign/@scheduleTimelines/ScheduleTimeline/@instances/ScheduledDecisionInstance/@epoch=StudyVersion/@studyDesigns/StudyDesign/@studyCells/StudyCell/@epoch</code></p></div>
