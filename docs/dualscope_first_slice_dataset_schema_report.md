# DualScope First Slice Dataset Schema Report

The schema checker validates:

- row count
- required fields
- empty prompts
- empty responses
- duplicate `example_id`
- split distribution

If the dataset file is missing, the verdict must be `blocked_by_missing_file`.
