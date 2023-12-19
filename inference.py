def get_inference_result(modelInput: dict):
  # DUMMY MODEL OUTPUT, REPLACE LATER
  modelOutput = [
      {
        "timestamp": 1702912245,
        "mortality": 20,
        "los": 40,
        "readmission": 21
      },
      {
        "timestamp": 1702912500,
        "mortality": 79,
        "los": 20,
        "readmission": 23
      },
      {
        "timestamp": 1702913000,
        "mortality": 32,
        "los": 75,
        "readmission": 43
      }
    ]
  return modelOutput