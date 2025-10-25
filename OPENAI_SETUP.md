# 🔑 OpenAI API Key Setup Guide

## Quick Setup

1. **Copy the environment template:**
   ```bash
   cp .env.template .env
   ```

2. **Get your OpenAI API key:**
   - Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
   - Click "Create new secret key"
   - Copy the key (starts with `sk-`)

3. **Add your API key to `.env`:**
   ```bash
   # Edit the .env file
   nano .env
   ```
   
   Replace `your-openai-api-key-here` with your actual API key:
   ```
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

4. **Start the application:**
   ```bash
   python frontend/app.py
   ```

## Environment Variables

The `.env` file supports these configuration options:

### Required
- `OPENAI_API_KEY`: Your OpenAI API key for GPT-4 integration

### Optional
- `OPENAI_MODEL`: AI model to use (default: `gpt-4-turbo`)
- `OPENAI_MAX_TOKENS`: Maximum response length (default: `2048`)
- `OPENAI_TEMPERATURE`: Response creativity (default: `0.7`)
- `APP_ENV`: Application environment (`development`, `production`)
- `DEBUG`: Enable debug mode (`true`, `false`)

## Alternative Setup Methods

### Method 1: Export in Terminal
```bash
export OPENAI_API_KEY="sk-your-api-key-here"
python frontend/app.py
```

### Method 2: Shell Profile (Permanent)
Add to `~/.zshrc` or `~/.bashrc`:
```bash
echo 'export OPENAI_API_KEY="sk-your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

### Method 3: UI Configuration
1. Start the app without an API key
2. Go to the "🤖 AI Copilot" tab
3. Enter your API key in the configuration section
4. Click "🔧 Configure AI"

## Security Notes

- ✅ The `.env` file is already in `.gitignore`
- ✅ Never commit API keys to version control
- ✅ Use environment variables in production
- ✅ Rotate your API keys regularly

## Testing AI Integration

Once configured, test the AI integration:

1. **Test Connection**: Use the "🧪 Test Connection" button
2. **Chat Test**: Ask "What's my system status?"
3. **Quick Analysis**: Try the performance analysis button

## Troubleshooting

### "AI not configured" error
- Check your API key is correctly set in `.env`
- Ensure the `.env` file is in the project root
- Verify the key starts with `sk-`

### "Connection failed" error
- Check your internet connection
- Verify your OpenAI account has API credits
- Ensure the API key is valid and not expired

### Import errors
- Make sure `python-dotenv` is installed: `pip install python-dotenv`
- Check the virtual environment is activated

## API Usage and Costs

- GPT-4-turbo pricing: ~$0.01-0.03 per request
- Typical analysis: ~1000-2000 tokens
- Monitor usage at [OpenAI Usage Dashboard](https://platform.openai.com/usage)

The AI copilot is now ready for intelligent system analysis! 🚀