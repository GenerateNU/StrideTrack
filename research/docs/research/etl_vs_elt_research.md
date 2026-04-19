**EXPLANATION OF ETL vs ELT**

**ETL** is primarily used when your transformations will take lots of compute power and not be something simple like converting 0s and 1s to false and true. For example, a case where you’re parsing through your data to extract fly times and other metrics more complicated than simple SQL transformations.

**ELT** would be used when you’re loading into something where you need minimal transformation power or something that has super-powerful in-house transformation capabilities.

**WHAT MAKES SENSE FOR US?**

In our case, an ETL pipeline makes significantly more sense. Our data is messy and requires lots of transformations, clearing of noisy, inaccurate pressure readings, the complete generation of a second foot’s data, and more. In this instance, it's more efficient to transform the data before loading it.

**SHOULD RAW DATA BE INCLUDED?**

Raw data should not in fact be included as it would be redundant for us since we wouldn't have a use case for it. The only usages we could think of would be finding fly/contact time which the transformed data includes. Therefore, it is best to not include the raw data at this moment.

______________________________________________________________________________________________________________

The runs table can include a coach_id for the uploaded run to populate the coach’s account with whatever runs they have uploaded.

**DEMO SQL FOR TABLES**

CREATE TABLE runs (\
  run_id      BIGSERIAL PRIMARY KEY,\
  user_id     BIGINT NOT NULL,\
  coach_id    BIGINT NOT NULL,\
  created_at  TIMESTAMP NOT NULL DEFAULT NOW(),\
  name        TEXT\
);

CREATE TABLE run_events (\
  event_id    BIGSERIAL PRIMARY KEY,\
  run_id      BIGINT NOT NULL REFERENCES runs(run_id) ON DELETE CASCADE,\
  start_time  NUMERIC NOT NULL,\
  end_time   NUMERIC NOT NULL,\
  foot        TEXT NOT NULL CHECK (foot IN ('LEFT','RIGHT')),\
  seq         INTEGER NOT NULL,\
  CHECK (end_time > start_time)\
);

**ACCESS TO INFORMATION ONLY GIVEN TO COACH WITH CORRECT ID**

SELECT\
re.event_id AS "Event ID",\
re.run_id AS "Run ID",\
re.start_time AS "Start Time",\
re.end_time AS "End Time",\
re.foot AS "Foot",\
re.seq AS "Sequence Number"\
FROM run_events AS re\
JOIN runs AS r ON re.run_id = r.run_id\
WHERE re.run_id = $run_id\
AND (r.coach_id = $user_id OR r.user_id = $user_id)\
ORDER BY seq;

**OPTIONAL*

We can either go by every other step or we can display the table by every contact step in the event. This is something we need to discuss and decide and we can modify accordingly.