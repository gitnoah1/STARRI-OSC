# minecraft-mcp

A Minecraft bot controlled by Claude over MCP (Model Context Protocol), built on [Mineflayer](https://github.com/PrismarineJS/mineflayer). Give Claude Desktop natural-language commands and it'll move, mine, build, fight, and chat in-game.

This is a personal fork/setup based on [yuniko-software/minecraft-mcp-server](https://github.com/yuniko-software/minecraft-mcp-server).

> [!IMPORTANT]
> Tested against Minecraft 1.21.11. Newer versions may not work until support is added.

## Prerequisites

- Git
- Node.js >= 20.10.0
- A running Minecraft world (Java Edition, singleplayer opened to LAN)
- Claude Desktop with Developer Mode enabled (Settings → Developer)

## Setup

```bash
git clone https://github.com/gitnoah1/mc-claudemcp.git
cd mc-claudemcp
npm install
npm run build
```

## Running

1. **Open your Minecraft world to LAN**
   In-game: `Esc → Open to LAN`. Note the port (default `25565`).

2. **Add the server to Claude Desktop's config**
   `Settings → Developer → Edit Config` opens `claude_desktop_config.json`. Add:

   ```json
   {
     "mcpServers": {
       "minecraft": {
         "command": "node",
         "args": ["C:\\Users\\vanes\\Downloads\\mc-claudemcp\\dist\\main.js"],
         "env": {
           "MINECRAFT_HOST": "localhost",
           "MINECRAFT_PORT": "25565",
           "MINECRAFT_USERNAME": "ClaudeBot"
         }
       }
     }
   }
   ```

   Adjust the path, host, and port to match your setup.

3. **Fully restart Claude Desktop** (quit from the tray, not just close the window).

4. Start a chat and tell Claude to do something in Minecraft — mentioning Minecraft in the prompt is what triggers the tool call and permission prompt.

## Available Tools

**Movement** — `get-position`, `move-to-position`, `look-at`, `jump`, `move-in-direction`
**Flight** — `fly-to`
**Inventory** — `list-inventory`, `find-item`, `equip-item`
**Blocks** — `place-block`, `dig-block`, `get-block-info`, `find-block`
**Furnace** — `smelt-item`
**Entities** — `find-entity`
**Chat** — `send-chat`, `read-chat`
**Game state** — `detect-gamemode`

## Notes

- First tool call after Claude Desktop boots can be slow — the MCP server is spinning up.
- Claude will ask permission before controlling the bot the first time each session.
- Works best with Claude Sonnet/Opus for more complex build requests (you can even feed it a reference image).

## Credits

Built on [mineflayer](https://github.com/PrismarineJS/mineflayer) 
ps bash your head agasit a rock love noah