from flask import Flask, render_template, request
import coc
import asyncio
from datetime import datetime, timezone
from urllib.parse import unquote

app = Flask(__name__)

EMAIL = "oceanshah86@gmail.com"
PASSWORD = "Ocean$&123"

@app.route("/", methods=["GET", "POST"])
def index():
    # Debug: Print all request parameters
    print(f"Request method: {request.method}")
    print(f"GET args: {request.args}")
    print(f"POST form: {request.form}")
    
    # Get clan tag from GET parameter or POST form (both use 'clan' now)
    # Handle URL encoding - decode the clan parameter
    clan_tag_raw = request.args.get('clan') or request.form.get('clan') or ""
    clan_tag = unquote(clan_tag_raw) if clan_tag_raw else ""
    print(f"Raw clan_tag: '{clan_tag_raw}'")
    print(f"Decoded clan_tag: '{clan_tag}'")
    
    # Only fetch data if a clan tag is provided
    if clan_tag:
        print(f"Fetching data for clan: {clan_tag}")
        # Fix for production environment with gunicorn
        try:
            # Try to get the current event loop
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # If no event loop is running, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        data = loop.run_until_complete(fetch_data(clan_tag))
    else:
        print("No clan tag provided, showing empty page")
        # Return empty data for initial page load
        data = {
            "clan_name": "",
            "enemy_name": "",
            "war_end_time": "",
            "time_remaining": "",
            "untouched_us": [],
            "untouched_enemy": [],
            "attackers_us": [],
            "attackers_enemy": [],
            "our_members": [],
            "enemy_members": []
        }
    
    return render_template("index.html", **data)

async def fetch_data(clan_tag):
    client = coc.Client(key_names="my-windows-keys", key_count=5)

    try:
        await client.login(EMAIL, PASSWORD)
        league_group = await client.get_league_group(clan_tag)

        if not league_group or not league_group.rounds:
            return {"error": "No CWL rounds found."}

        current_war = None
        # Look through all rounds to find a war that includes our clan
        for round in league_group.rounds:
            for war_tag in round:
                if war_tag == "#0":
                    continue
                war = await client.get_league_war(war_tag)
                if war.state == "inWar":
                    # Check if this war includes our clan
                    if (war.clan.tag == clan_tag or war.opponent.tag == clan_tag):
                        current_war = war
                        break
            if current_war:
                break

        if not current_war:
            return {"error": f"No ongoing CWL war found for clan {clan_tag}."}

        # Determine which side our clan is on
        if current_war.clan.tag == clan_tag:
            # Our clan is the clan side
            our_clan = current_war.clan
            enemy_clan = current_war.opponent
        else:
            # Our clan is the opponent side
            our_clan = current_war.opponent
            enemy_clan = current_war.clan

        clan_name = our_clan.name
        enemy_name = enemy_clan.name

        # Calculate time remaining - handle timezone properly
        war_end_time = current_war.end_time.time
        current_time = datetime.now(timezone.utc)
        
        # Ensure both times are timezone-aware
        if war_end_time.tzinfo is None:
            # If war_end_time is naive, assume it's UTC
            war_end_time = war_end_time.replace(tzinfo=timezone.utc)
        
        time_remaining = war_end_time - current_time
        
        # Format time remaining
        if time_remaining.total_seconds() > 0:
            hours = int(time_remaining.total_seconds() // 3600)
            minutes = int((time_remaining.total_seconds() % 3600) // 60)
            time_remaining_str = f"{hours}h {minutes}m remaining"
        else:
            time_remaining_str = "War ended"

        # Get attacked bases for both sides
        attacked_our_bases = {atk.defender_tag for m in enemy_clan.members for atk in m.attacks}
        attacked_enemy_bases = {atk.defender_tag for m in our_clan.members for atk in m.attacks}

        # Find untouched bases
        untouched_us = [m for m in our_clan.members if m.tag not in attacked_our_bases]
        untouched_enemy = [m for m in enemy_clan.members if m.tag not in attacked_enemy_bases]

        # Find attackers with remaining attacks
        attackers_us = [(m.name, 1 - len(m.attacks)) for m in our_clan.members if 1 - len(m.attacks) > 0]
        attackers_enemy = [(m.name, 1 - len(m.attacks)) for m in enemy_clan.members if 1 - len(m.attacks) > 0]

        # Sort members by map position for proper base numbering
        untouched_us_sorted = sorted(untouched_us, key=lambda x: x.map_position)
        untouched_enemy_sorted = sorted(untouched_enemy, key=lambda x: x.map_position)

        # Get all members sorted by map position for dropdown lists
        our_members = sorted(our_clan.members, key=lambda x: x.map_position)
        enemy_members = sorted(enemy_clan.members, key=lambda x: x.map_position)

        # Get attackers with remaining attacks, sorted by map position
        attackers_us_with_pos = [(m.name, 1 - len(m.attacks), m.map_position, m.town_hall)
                                for m in our_clan.members if 1 - len(m.attacks) > 0]
        attackers_us_with_pos.sort(key=lambda x: x[2])  # Sort by map position

        attackers_enemy_with_pos = [(m.name, 1 - len(m.attacks), m.map_position, m.town_hall)
                                   for m in enemy_clan.members if 1 - len(m.attacks) > 0]
        attackers_enemy_with_pos.sort(key=lambda x: x[2])  # Sort by map position

        return {
            "clan_name": clan_name,
            "enemy_name": enemy_name,
            "war_end_time": war_end_time.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "time_remaining": time_remaining_str,
            "untouched_us": untouched_us_sorted,
            "untouched_enemy": untouched_enemy_sorted,
            "attackers_us": attackers_us_with_pos,
            "attackers_enemy": attackers_enemy_with_pos,
            "our_members": our_members,
            "enemy_members": enemy_members
        }

    except Exception as e:
        return {"error": str(e)}
    finally:
        try:
            await client.close()
        except Exception as e:
            print(f"Error closing client: {e}")
            # Ignore close errors in production

if __name__ == "__main__":
    app.run(debug=True)