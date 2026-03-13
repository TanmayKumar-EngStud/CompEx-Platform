# Prisma Directory

This directory contains the database schema definition, migrations, and database-related utilities.

## Structure

* **schema.prisma**: Database schema definition
* **migrations/**: Database migration files
* **seeds/**: Database seeding scripts
* **queries/**: Complex raw queries (if needed)

## Database Schema

The schema defines the following key models:

### Problems

Questions with metadata, options, and solutions:
- `id`: Unique identifier
- `title`: Question title
- `content`: Question content (supports LaTeX)
- `options`: Answer options (for multiple choice)
- `solution`: Solution explanation
- `examTypeId`: Reference to exam type
- `sectionId`: Reference to section
- `tags`: Many-to-many relation to tags

### ExamTypes

Different exam types (GRE, GMAT, CAT):
- `id`: Unique identifier
- `name`: Exam name
- `sections`: One-to-many relation to sections

### Sections

Exam sections (Quants, Verbal, etc.):
- `id`: Unique identifier
- `name`: Section name
- `examTypeId`: Reference to exam type

### Tags

Question categorization:
- `id`: Unique identifier
- `name`: Tag name
- `problems`: Many-to-many relation to problems

### UserAttempts

Tracks user answers:
- `id`: Unique identifier
- `userId`: Reference to user
- `problemId`: Reference to problem
- `answer`: User's answer
- `isCorrect`: Correctness flag
- `timeSpent`: Time spent on question

## Integration with Application

- Prisma client is used in API routes to query the database
- Models are referenced in TypeScript types
- Migrations are run during deployment
- Seeds are used for development and testing

## Commands

```bash
# Generate Prisma client
npx prisma generate

# Run migrations
npx prisma migrate dev

# Reset database (development only)
npx prisma migrate reset

# Seed database
pnpm seed

# Open Prisma Studio
npx prisma studio
```