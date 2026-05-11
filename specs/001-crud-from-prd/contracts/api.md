# API Contract: PRD CRUD Generation

## POST /generate

**Description**: Upload a PRD file and generate a runnable Spring Boot starter project ZIP.

### Request

- Content-Type: `multipart/form-data`
- Body:
  - `file`: PRD file to upload

### Response

- `200 OK`
- JSON body:
  - `zip_file`: string path to the generated ZIP archive

### Example

Request:
```http
POST /generate HTTP/1.1
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="requirements.txt"
Content-Type: text/plain

<PRD content>
------WebKitFormBoundary--
```

Response:
```json
{
  "zip_file": "output/project.zip"
}
```

## Behavior

- The endpoint reads the uploaded file and passes its text to the pipeline.
- The analyzer extracts entities, fields, and CRUD intent from PRD text.
- The generator renders Spring Boot source files and bundles them into `output/project.zip`.
