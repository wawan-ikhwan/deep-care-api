# Deepcare API

[![API Version](https://img.shields.io/badge/API%20Version-v1.0-blue.svg)](https://deepcare-api-he4vzldwiq-et.a.run.app)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)

## Introduction

Welcome to the Deepcare API! This API offers predictive analytics for healthcare outcomes, providing probabilities for specific patient scenarios, including:

- **Readmission Probability (within 30 days):** This endpoint predicts the likelihood of a patient being readmitted within 30 days of discharge.

- **Prolonged Length of Stay Probability (greater than 4 days):** Determine the probability of a patient having an extended hospital stay beyond 4 days.

- **Mortality in Hospital Probability:** Predict the likelihood of mortality during a patient's hospital stay.

These predictions are based on advanced machine learning models trained on comprehensive healthcare datasets.

## Documentation

Visit [Deepcare API Postman Documentation](https://documenter.getpostman.com/view/16311653/2s9YkocM2o) for detailed information.

### Endpoints

- **`POST /register`**: Register a new user.
- **`POST /login`**: Log in and obtain an authentication token.
- **`POST /inference`**: Perform healthcare outcome inference.

### Authentication

To access Deepcare API, follow the authentication flow:

1. **Register a new user**: Use the `POST /register` endpoint to create a new user account.

   Example Register Request:
   ```json
   {
     "name": "Capstone",
     "email": "capstone@bangkit.academy",
     "password": "sensitive"
   }
   ```

    Example Register Response:
    ```json
    {
    "error": false,
    "message": "Successfully stored in the database!"
    }
    ```
2. **Log in**: Use the `POST /login` endpoint with your credentials to obtain an authentication token.

   Example Login Request:
   ```json
    {
      "email": "capstone@bangkit.academy",
      "password": "sensitive"
    }
   ```

    Example Login Response:
    ```json
    {
      "error": false,
      "message": "Success",
      "loginResult": {
        "name": "Capstone",
        "userId": "M4LWhC2H82WOVPo2mZpNAlMr58g1",
        "token": "your_authentication_token",
        "isLogin": true
      }
    }
    ```

3. **Healthcare Outcome Inference**: Use the `POST /inference` endpoint to perform healthcare outcome inference.

    Example Inference Request:
    ```json
    {
      "admission_id": 29999625,
      "timestamp": 5928123600,
      "token": "your_authentication_token",
      "model_input": {
        "arterialbloodpressuremean": "106.0",
        "heartrate": "97.0",
        // Include other relevant model input parameters, see Postman Docs.
      }
    }
    ```

    Example Inference Response:
    ```json
    {
      "admission_id": 29999625,
      "caregiver": "Capstone",
      "model_output": [
        {
          "los": 72.15,
          "mortality": 70.84,
          "readmission": 63.76,
          "timestamp": "5928033660"
        },
        // Include other relevant model output entries
      ]
    }
    ```

### Rate Limiting

To prevent abuse, Deepcare API has rate limiting in place 5 requests/sec.

### Error Handling

Errors in Deepcare API follow a standardized format. For details on error responses and common scenarios, refer to the error handling section in code.

## Getting Started

To get started with Deepcare API, follow these steps:

### Prerequisites

Before using Deepcare API, ensure you have the following in `requirements.txt`

### Installation

To install the Deepcare API SDK, follow these steps:

1. **Create a Virtual Environment:**

   ```bash
   python -m venv .venv
   ```

2. **Activate the Virtual Environment:**
    * On Windows:
    ```powershell
    .venv\Scripts\activate
    ```
    * On Linux:
    ```bash
    source .venv/bin/activate
    ```
3. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Copy Environment Variables:**
    ```
    cp .env.example .env
    ```
    Modify the values in the .env file according to your API configuration.

## Support
If you encounter any issues or have questions, reach out to our support team at [ch2-ps589@bangkit.academy@bangkit.academy](ch2-ps589@bangkit.academy@bangkit.academy)

## Contributing

We welcome contributions! Whether it's bug reports, feature requests, or code contributions.

## License
Deepcare API is licensed under the MIT License - see the LICENSE file for details.
