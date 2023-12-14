Wikipedia Telegram Bot

A Telegram bot built with Python that utilizes the Wikipedia API to fetch information based on user queries. The bot supports language translation and user search history management.

Features
Information Retrieval: Utilizes Wikipedia's API to fetch article summaries.
Translation Support: Provides translation of retrieved content to various languages.
Search History: Keeps track of user search history and allows clearing of history.
Installation
Clone the repository:

```bash
git clone https://github.com/your-username/telegram-wikipedia-bot.git
cd telegram-wikipedia-bot
```
Install dependencies:

```bash
pip install -r requirements.txt
```
Set up environment variables:
Create a .env file with the following content:

.env
```bash
BOT_TOKEN=your_telegram_bot_token
# Add any other necessary tokens here
```
Run the bot:


```bash
python bot.py
```
Usage
Start the bot: Send a message or use the ```/start``` command.
Query Wikipedia: Enter your search query, and the bot will fetch information.
Language Translation: Use inline buttons to translate content to different languages.
Search History: View your search history with the /history command.
Contributions
Contributions, bug reports, and feature requests are welcome! Feel free to open issues or submit pull requests.

License
This project is licensed under the MIT License.

