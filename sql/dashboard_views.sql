
-- Global Weather and Demographics Dashboard
-- Dashboard views for Looker Studio.
-- Source table: current_weather_stats

-- 1. City-level data for the map, filters and detailed table.
CREATE OR REPLACE VIEW
  `noted-amphora-512320-t4.global_weather_data.vw_city_weather_dashboard`
AS
SELECT
  City,
  Country,
  Population,
  Latitude,
  Longitude,
  Temperature,
  Temperature_Fahrenheit,
  Wind_Speed,
  Temperature_Category
FROM
  `noted-amphora-512320-t4.global_weather_data.current_weather_stats`;


-- 2. Country-level temperature comparison.
-- Population represents recorded city populations, not national populations.
CREATE OR REPLACE VIEW
  `noted-amphora-512320-t4.global_weather_data.vw_country_weather_summary`
AS
SELECT
  Country,
  ROUND(AVG(Temperature), 2) AS Average_Temperature_C,
  ROUND(MAX(Temperature), 2) AS Highest_Temperature_C,
  ROUND(MIN(Temperature), 2) AS Lowest_Temperature_C,
  ROUND(AVG(Wind_Speed), 2) AS Average_Wind_Speed,
  SUM(Population) AS Population_Of_Recorded_Cities,
  COUNT(*) AS Cities_Recorded
FROM
  `noted-amphora-512320-t4.global_weather_data.current_weather_stats`
GROUP BY
  Country;


-- 3. Temperature category distribution.
CREATE OR REPLACE VIEW
  `noted-amphora-512320-t4.global_weather_data.vw_temperature_distribution`
AS
SELECT
  Temperature_Category,
  COUNT(*) AS Number_Of_Cities,
  ROUND(
    100.0 * COUNT(*) / SUM(COUNT(*)) OVER (),
    1
  ) AS Percentage_Of_Cities
FROM
  `noted-amphora-512320-t4.global_weather_data.current_weather_stats`
GROUP BY
  Temperature_Category;


-- 4. Hottest and coldest city rankings.
CREATE OR REPLACE VIEW
  `noted-amphora-512320-t4.global_weather_data.vw_city_temperature_rankings`
AS
WITH ranked_cities AS (
  SELECT
    City,
    Country,
    Temperature,
    Temperature_Fahrenheit,
    Temperature_Category,
    ROW_NUMBER() OVER (
      ORDER BY Temperature DESC, City
    ) AS Hottest_Rank,
    ROW_NUMBER() OVER (
      ORDER BY Temperature ASC, City
    ) AS Coldest_Rank
  FROM
    `noted-amphora-512320-t4.global_weather_data.current_weather_stats`
)
SELECT
  City,
  Country,
  Temperature,
  Temperature_Fahrenheit,
  Temperature_Category,
  Hottest_Rank,
  Coldest_Rank,
  'Hottest' AS Ranking_Type
FROM ranked_cities
WHERE Hottest_Rank <= 10

UNION ALL

SELECT
  City,
  Country,
  Temperature,
  Temperature_Fahrenheit,
  Temperature_Category,
  Hottest_Rank,
  Coldest_Rank,
  'Coldest' AS Ranking_Type
FROM ranked_cities
WHERE Coldest_Rank <= 10;


-- 5. KPI values for the dashboard header.
CREATE OR REPLACE VIEW
  `noted-amphora-512320-t4.global_weather_data.vw_weather_kpis`
AS
SELECT
  COUNT(*) AS Total_Cities,
  ROUND(AVG(Temperature), 2) AS Average_Temperature_C,
  ROUND(AVG(Temperature_Fahrenheit), 2)
    AS Average_Temperature_F,
  ARRAY_AGG(
    STRUCT(City, Country, Temperature)
    ORDER BY Temperature DESC, City
    LIMIT 1
  )[SAFE_OFFSET(0)] AS Hottest_City,
  ARRAY_AGG(
    STRUCT(City, Country, Temperature)
    ORDER BY Temperature ASC, City
    LIMIT 1
  )[SAFE_OFFSET(0)] AS Coldest_City
FROM
  `noted-amphora-512320-t4.global_weather_data.current_weather_stats`;
