# QA Checklist

- [x] API create/list/read/update/delete paths are exercised by `python3 -m unittest discover -s backend/tests -v`.
- [x] Validation error for empty title is covered with a `400 Bad Request` response.
- [x] Missing note id returns `404 Not Found`.
- [x] Database-backed repository behavior was revalidated before recording API evidence with `python3 -m unittest discover -s tests -v`.
- [x] DB -> API ordering was respected: the database gate was already green before API validation was recorded.
- [x] No external dependencies, cloud resources, or deployment changes were added.
- [x] Frontend, visual, and E2E validation are explicitly deferred to the UI task and therefore marked not applicable here.
- [x] Branch conflict guard was run and documented as a blocking implementation lease conflict for the code paths owned by another active branch.
