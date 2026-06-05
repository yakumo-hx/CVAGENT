# Security

## API Keys

Never commit real API keys. Use `.env` locally or paste the key into the app settings page.

The repository includes only `.env.example`:

```text
DEEPSEEK_API_KEY=your_key_here
```

## Local Data

The following paths are ignored by git:

- `.env`
- local databases
- logs
- uploads
- exports
- `.local_research_archive/`

## User Data

Resume and JD content can contain sensitive personal information. Treat all user-provided files as private. Do not add real resumes, real job descriptions, platform cookies, browser profiles, or scraped data to this repository.

## Reporting Issues

If you find a privacy or security issue, open a GitHub issue with a minimal reproduction that does not include personal data.
