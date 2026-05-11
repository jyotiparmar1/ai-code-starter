# Data Model: PRD CRUD Inference

## Entities

- **Entity**: A domain concept extracted from the PRD, such as `Customer`, `Order`, or `Product`.
  - `name`: entity class name
  - `fields`: list of field definitions with `name` and `type`
  - `operations`: list of inferred CRUD actions

## Fields

- **Field**: A typed property belonging to an entity.
  - `name`: field identifier
  - `type`: Java-compatible type name (e.g. `String`, `Long`, `Integer`, `Boolean`)

## CRUD Operations

- **Operation**: A behavior inferred from PRD semantics.
  - `type`: one of `CREATE`, `READ`, `UPDATE`, `DELETE`
  - `method`: HTTP method inferred, such as `GET`, `POST`, `PUT`, `DELETE`
  - `endpoint`: API path, such as `/orders` or `/customers/{id}`
  - `description`: optional natural-language description of the operation

## API Contract Model

- **API**: A generated endpoint mapping that connects inferred operations to controller methods.
  - `endpoint`: non-empty path string
  - `method`: HTTP method
  - `entity`: referenced entity name
  - `operation`: operation type

## Generated Artifact Model

- **GeneratedArtifact**: Output files created from templates.
  - `Application.java`
  - `application.properties`
  - `pom.xml`
  - `entity/{Entity}.java`
  - `repository/{Entity}Repository.java`
  - `service/{Entity}Service.java`
  - `controller/{Entity}Controller.java`
  - `inference-summary.txt` or README notes
