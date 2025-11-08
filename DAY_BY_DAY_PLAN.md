# Day-by-day plan (7 days)

Pick exact times that fit you

## Day 1 — (you’ve done most of this)

- Create DynamoDB table + GSI (done).
- Create process_emission Lambda, fix dependencies, test via CLI (done).
- Confirm CloudWatch logs working (done).

## Day 2 — Create city fetch Lambda + schedule (today / tomorrow)

- Deploy fetch_city_data Lambda (code I provided earlier).
- Add env var OPENWEATHER_KEY.
- Manually run Lambda, confirm DynamoDB entries for city_... users.
- Create EventBridge rule: run every 5 minutes → target fetch_city_data.
- Verify items appear in DynamoDB every run.

## Day 3 — Create small scan_dynamodb Lambda + API Gateway

- Implement scan_dynamodb Lambda: scans SmartCityEmissions, returns JSON array (clean up Decimal to str).
- Create API Gateway REST API (or HTTP API) with:
  - GET /fetch → scan_dynamodb
  - POST /submit → process_emission
- Enable CORS on both methods.
- Test both endpoints with curl or browser.

## Day 4 — Connect and test webpage locally

- Update smartcity_dashboard.html with real SUBMIT_URL and FETCH_URL.
- Open file locally in browser (double-click), run test submit and fetch; examine charts.
- Debug CORS or JSON issues.

## Day 5 — Tableau

- Export DynamoDB -> CSV (small script) or use scan_dynamodb Lambda to produce CSV.
- Build Tableau dashboard: 3 sheets (temperature trend per city, current city temps, CO₂ by user), add filters and a title.
- Export screenshots and add to report.

## Day 6 — Documentation & polishing

- Write README: architecture diagram, environment variables, how to run locally, commands used.
- Prepare demo script (what to click, sample inputs, what to say).
# Day-by-day plan (7 days)

Pick exact times that fit you

## Current status (checked)

- [x] AWS account created and CLI configured
- [x] IAM users exist (you showed the IAM Users screen)
- [x] DynamoDB table `SmartCityEmissions` created and moved to ACTIVE
- [x] Global Secondary Index `CityActivityIndex` added and ACTIVE
- [x] Lambda `process_emission` created and deployed (handler/import issues fixed)
- [x] Fixed missing dependencies (packaged `requests`) and uploaded deployable zip
- [x] Verified Lambda runs and writes to DynamoDB (CloudWatch logs confirmed)
- [x] Packaging steps documented: `pip install -t package/` → zip → upload
- [x] You provided `smartcity_dashboard.html` (ready-to-run single-file webpage)
- [x] Architecture for city fetcher Lambda and EventBridge scheduler designed

## Day 1 — (you’ve done most of this)

- [x] Create DynamoDB table + GSI.
- [x] Create `process_emission` Lambda, fix dependencies, test via CLI.
- [x] Confirm CloudWatch logs working.

## Day 2 — Create city fetch Lambda + schedule (today / tomorrow)

- [ ] Deploy `fetch_city_data` Lambda (code provided earlier).
- [ ] Add env var `OPENWEATHER_KEY`.
- [ ] Manually run Lambda, confirm DynamoDB entries for `city_...` users.
- [ ] Create EventBridge rule: run every 5 minutes → target `fetch_city_data`.
- [ ] Verify items appear in DynamoDB every run.

## Day 3 — Create small scan_dynamodb Lambda + API Gateway

- [ ] Implement `scan_dynamodb` Lambda: scans `SmartCityEmissions`, returns JSON array (clean up Decimal to str).
- [ ] Create API Gateway REST API (or HTTP API) with:
  - GET /fetch → `scan_dynamodb`
  - POST /submit → `process_emission`
- [ ] Enable CORS on both methods.
- [ ] Test both endpoints with curl or browser.

## Day 4 — Connect and test webpage locally

- [x] `smartcity_dashboard.html` ready-to-run (file provided).
- [ ] Update `smartcity_dashboard.html` with real `SUBMIT_URL` and `FETCH_URL`.
- [ ] Open file locally in browser, run test submit and fetch; examine charts.
- [ ] Debug CORS or JSON issues.

## Day 5 — Tableau

- [ ] Export DynamoDB -> CSV (small script) or use `scan_dynamodb` Lambda to produce CSV.
- [ ] Build Tableau dashboard: 3 sheets (temperature trend per city, current city temps, CO₂ by user), add filters and a title.
- [ ] Export screenshots and add to report.

## Day 6 — Documentation & polishing

- [ ] Write README: architecture diagram, environment variables, how to run locally, commands used.
- [ ] Prepare demo script (what to click, sample inputs, what to say).
- [ ] Add comments in Lambdas.

## Day 7 — Final testing & submission

- [ ] Do full end-to-end test: submit emission from webpage, check DynamoDB, see updated charts, check Tableau screenshots.
- [ ] Make final minor fixes and prepare zipped project and slides (if needed).
