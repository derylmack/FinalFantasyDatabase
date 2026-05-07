"""
Main Flask applicatoin for FFXIV Database.
Defines the app factory, initializes extentions, and sets up routes.
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from config import Config
from models import db, Server, Character, StorageLocations, Items, ItemLocations
from models import CharactersJobLevels, Jobs
from sqlalchemy.orm import joinedload

def create_app(config_class=Config):
    """ Base call for the ffxivdatabase app
    Args:
        configuration file

    Returns:
        int
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize the database with the app
    db.init_app(app)

    @app.route('/')
    @app.route('/characters')


    def characters():
        """Display a list of all characters from the database."""
        chars = Character.query.all() #Gets all characters from the database
        servers = Server.query.order_by(Server.Server_Name).all()
        return render_template('characters.html',
                               title='My FFXIV Characters',
                               characters=chars,
                               servers=servers)

    @app.route('/add_character', methods=['POST'])
    def add_character():
        if request.method == 'POST':
            try:
                # Get data from form
                character_name = request.form.get('character_name').strip()
                server_id = int(request.form.get('server_id'))
                playable = 'playable' in request.form # checkbox returns value only if checked

                #Basic validation
                if not character_name:
                    flash('Character name is required!', 'error')
                    return redirect(url_for('characters'))

                #Create new Character object
                new_character = Character(
                    Character_Name=character_name,
                    Server_ID=server_id,
                    Playable=playable
                )

                # Add  to database and commit
                db.session.add(new_character)
                db.session.commit()

                flash(f'Character "{character_name}" added successfully!', 'success')

            except ValueError:
                flash('Invalid server selection.', 'error')
            # pylint: disable=broad-exception-caught
            except Exception as e:
                flash(f'Error: {str(e)}', 'error')

        # Always redirect back to the characters list
        return redirect(url_for('characters'))

    @app.route('/character/<int:char_id>')
    def character_detail(char_id):
        """Display details for a specific character."""
        # Gets the character with the given ID or returns 404
        character = Character.query.options(
            joinedload(Character.server),
            joinedload(Character.storage_locations)
                .joinedload(StorageLocations.item_locations)
                .joinedload(ItemLocations.item),
            joinedload(Character.characters_job_levels)
                .joinedload(CharactersJobLevels.job)
        ).get_or_404(char_id)

        storages = StorageLocations.query.filter_by(Character_ID=char_id)\
            .order_by(StorageLocations.Storage_Location).all()

        # Optional: Pre-load items for each storage (you can do it here or in template)

        return render_template('character_detail.html',
                               title=f"{character.Character_Name}'s Details",
                               character=character,
                               storages=storages)

    @app.route('/add_storage_location/<int:char_id>', methods=['POST'])
    def add_storage_location(char_id):
        """Add a new storage location for a specific character"""
        if request.method == 'POST':
            try:
                location_name = request.form.get('storage_location').strip()

                if not location_name:
                    flash('Storage location name is required!', 'error')
                    return redirect(url_for('character_detail', char_id=char_id))

                # Create new StorageLocations record
                new_storage = StorageLocations(
                    Character_ID=char_id,
                    Storage_Location=location_name
                )

                db.session.add(new_storage)
                db.session.commit()

                flash(f'Storage location "{location_name}" added successfully!', 'success')

            # pylint: disable=broad-exception-caught
            except Exception as e:
                db.session.rollback()
                flash(f'Error adding storage locations: {str(e)}', 'error')
        return redirect(url_for('character_detail', char_id=char_id))

    @app.route('/servers')
    def servers():
        """Display a list of all servers from the database."""
        servers = Server.query.order_by(Server.Server_Name).all()
        return render_template('servers.html',
                               title='FFXIV Servers',
                               servers=servers)

    @app.route('/seed_jobs')
    def seed_jobs():
        """ Seed the Jobs table with FFXIV job data. """
        try:
            jobs_data = [
                # Tanks
                {"longname": "Paladin", "shortname": "PLD", "starting": 1, "limited": False, "type": "Tank"},
                {"longname": "Warrior", "shortname": "WAR", "starting": 1, "limited": False, "type": "Tank"},
                {"longname": "Dark Knight", "shortname": "DRK", "starting": 30, "limited": False, "type": "Tank"},
                {"longname": "Gunbreaker", "shortname": "GNB", "starting": 60, "limited": False, "type": "Tank"},

                # Healers
                {"longname": "White Mage", "shortname": "WHM", "starting": 1, "limited": False, "type": "Healer"},
                {"longname": "Scholar", "shortname": "SCH", "starting": 1, "limited": False, "type": "Healer"},
                {"longname": "Astrologian", "shortname": "AST", "starting": 30, "limited": False, "type": "Healer"},
                {"longname": "Sage", "shortname": "SGE", "starting": 70, "limited": False, "type": "Healer"},

                # Melee DPS
                {"longname": "Monk", "shortname": "MNK", "starting": 1, "limited": False, "type": "Melee"},
                {"longname": "Dragoon", "shortname": "DRG", "starting": 1, "limited": False, "type": "Melee"},
                {"longname": "Ninja", "shortname": "NIN", "starting": 1, "limited": False, "type": "Melee"},
                {"longname": "Samurai", "shortname": "SAM", "starting": 50, "limited": False, "type": "Melee"},
                {"longname": "Reaper", "shortname": "RPR", "starting": 70, "limited": False, "type": "Melee"},
                {"longname": "Viper", "shortname": "VIP", "starting": 80, "limited": False, "type": "Melee"},

                # Ranged Physical
                {"longname": "Bard", "shortname": "BRD", "starting": 1, "limited": False, "type": "Ranged"},
                {"longname": "Machinist", "shortname": "MCH", "starting": 30, "limited": False, "type": "Ranged"},
                {"longname": "Dancer", "shortname": "DNC", "starting": 60, "limited": False, "type": "Ranged"},

                # Magical Ranged
                {"longname": "Black Mage", "shortname": "BLM", "starting": 1, "limited": False, "type": "Caster"},
                {"longname": "Summoner", "shortname": "SMN", "starting": 1, "limited": False, "type": "Caster"},
                {"longname": "Red Mage", "shortname": "RDM", "starting": 1, "limited": False, "type": "Caster"},
                {"longname": "Blue Mage", "shortname": "BLU", "starting": 1, "limited": True, "type": "Caster"},

                # Crafting
                {"longname": "Carpenter", "shortname": "CRP", "starting": 1, "limited": False, "type": "Crafting"},
                {"longname": "Blacksmith", "shortname": "BSM", "starting": 1, "limited": False, "type": "Crafting"},
                {"longname": "Armorer", "shortname": "ARM", "starting": 1, "limited": False, "type": "Crafting"},
                {"longname": "Goldsmith", "shortname": "GSM", "starting": 1, "limited": False, "type": "Crafting"},
                {"longname": "Leatherworker", "shortname": "LTW", "starting": 1, "limited": False, "type": "Crafting"},
                {"longname": "Weaver", "shortname": "WVR", "starting": 1, "limited": False, "type": "Crafting"},
                {"longname": "Alchemist", "shortname": "ALC", "starting": 1, "limited": False, "type": "Crafting"},
                {"longname": "Culinarian", "shortname": "CUL", "starting": 1, "limited": False, "type": "Crafting"},

                # Gathering
                {"longname": "Miner", "shortname": "MIN", "starting": 1, "limited": False, "type": "Gathering"},
                {"longname": "Botanist", "shortname": "BTN", "starting": 1, "limited": False, "type": "Gathering"},
                {"longname": "Fisher", "shortname": "FSH", "starting": 1, "limited": False, "type": "Gathering"},
            ]

            added = 0
            for data in jobs_data:
                existing = Jobs.query.filter_by(Job_Longname=data["longname"]).first()
                if not existing:
                    new_job = Jobs(
                        Job_Longname=data["longname"],
                        Job_Shortname=data["shortname"],
                        Starting_Level=data["starting"],
                        Limited_Job=data["limited"],
                        Job_Type=data["type"]
                    )
                    db.session.add(new_job)
                    added += 1

            db.session.commit()
            flash(f'Successfully seeded {added} new jobs.', 'success')

        # pylint: disable=broad-exception-caught
        except Exception as e:
            db.session.rollback()
            flash(f'Error seeding jobs: {str(e)}', 'error')

        return redirect(url_for('jobs_list'))

    @app.route('/seed_character_job_levels')
    def seed_character_job_levels():
        """ Populate CharactersJobLevels for all playable characters"""
        try:
            # Get all playable characters
            characters = Character.query.filter_by(Playable=True).all()

            # Get all jobs
            all_jobs = Jobs.query.all()

            added = 0
            for char in characters:
                for job in all_jobs:
                    # check if entry already exists
                    existing = CharactersJobLevels.query.filter_by(
                        Character_ID=char.Character_ID,
                        Job_ID=job.Job_ID
                    ).first()

                    if not existing:
                        new_entry = CharactersJobLevels(
                            Character_ID=char.Character_ID,
                            Job_ID=job.Job_ID,
                            Job_Level=0   # 0 = not unlocked yet
                        )
                        db.session.add(new_entry)
                        added += 1

            db.session.commit()
            flash(f'Successfully added {added} character-job entries.', 'success')

        # pylint: disable=broad-exception-caught
        except Exception as e:
            db.session.rollback()
            flash(f'Error seeding character job levels: {str(e)}', 'error')

        return redirect(url_for('characters'))

    @app.route('/items')
    def items_list():
        """ Display all items with search functionality """
        search_query = request.args.get('search', '').strip()

        query = Items.query

        if search_query:
            query = query.filter(Items.Item_Name.ilike(f'%{search_query}%'))

        all_items = query.order_by(Items.Item_Name).all()

        return render_template('items.html',
                               title='All Items',
                               items=all_items,
                               search_query=search_query)

    @app.route('/jobs')
    def jobs_list():
        """Display all jobs in the game."""
        all_jobs = Jobs.query.order_by(Jobs.Job_Type, Jobs.Job_Longname).all()
        return render_template('jobs.html',
                               title='FFXIV Jobs',
                               jobs=all_jobs)

    # pylint: disable=unused-variable
    @app.route('/edit_character/<int:char_id>')
    def edit_character(char_id):
        """ Edit an existing character. """
        character = Character.query.get_or_404(char_id)
        servers = Server.query.order_by(Server.Server_Name).all()

        if request.method == 'POST':
            try:
                character.Character_Name = request.form.get('character_name').strip()
                character.Server_ID = int(request.form.get('server_id'))
                character.Playable = 'playable' in request.form

                db.session.commit()
                flash(f'Character "{character.Character_Name}" updated successfully!', 'success')
                return redirect(url_for('characters'))

            # pylint: disable=broad-exception-caught
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating character: {str(e)}', 'error')

        return render_template('edit_character.html',
                               character=character,
                               servers=servers,
                               title=f" Edit {character.Character_Name}")

    # pylint: disable=unused-variable
    @app.route('/delete_character/<int:char_id>', methods=['POST'])
    def delete_character(char_id):
        """Delete a character from the database."""
        character = Character.query.get_or_404(char_id)

        try:
            db.session.delete(character)
            db.session.commit()
            flash(f'Character "{character.Character_Name}" had been deleted.', 'success')

        # pylint: disable=broad-exception-caught
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting character: {str(e)}', 'error')
        return redirect(url_for('characters'))

    @app.route('/update_job_level/<int:char_id>/<int:job_id>', methods=['POST'])
    def update_job_level(char_id, job_id):
        try:
            new_level = int(request.form.get('job_level', 0))

            # Find or create the CharactersJobLevels entry
            job_entry = CharactersJobLevels.query.filter_by(
                Character_ID=char_id,
                Job_ID=job_id
            ).first()

            if not job_entry:
                # Create new entry if character doesn't have the job yet
                job_entry = CharactersJobLevels(
                    Character_ID=char_id,
                    Job_ID=job_id,
                    Job_Level=new_level
                )
                db.session.add(job_entry)
            else:
                job_entry.Job_Level = new_level

            db.session.commit()
            flash('Job level updated successfully.', 'success')

        except ValueError:
            flash('Invalid level updated successfully!', 'error')
        # pylint: disable=broad-exception-caught
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating job level: {str(e)}', 'error')

        return redirect(url_for('character_detail', char_id=char_id))

    # pylint: disable=unused-variable
    @app.route('/add_item_to_storage/<int:storage_id>', methods=['POST'])
    def add_item_to_storage(storage_id):
        """Add an item to a specific storage location."""
        try:
            item_name = request.form.get('item_name').strip()
            quantity = int(request.form.get('quantity', 1))
            is_hq = 'hq' in request.form
            char_id = int(request.form.get('char_id'))

            if not item_name:
                flash('Item name is required!', 'error')
                return redirect(url_for('character_detail', char_id=request.args.get('char_id')))

            if not char_id:
                flash('Character ID missing.', 'error')
                return redirect(url_for('characters'))

            item = Items.query.filter(Items.Item_Name.ilike(item_name)).first()

            if not item:
                item = Items(Item_Name=item_name)
                db.session.add(item)
                db.session.flush() # Get the new Item_ID

            # Check if this item is already in this storage
            existing = ItemLocations.query.filter_by(
                Item_ID=item.Item_ID,
                Storage_ID=storage_id
            ).first()

            if existing:
                if is_hq:
                    existing.Quantity_HQ = (existing.Quantity_HQ or 0) + quantity
                else:
                    existing.Quantity = (existing.Quantity or 0) + quantity
            else:
                new_item_loc = ItemLocations(
                    Item_ID=item.Item_ID,
                    Storage_ID=storage_id,
                    Quantity=0 if is_hq else quantity,
                    Quantity_HQ=quantity if is_hq else 0
                )
                db.session.add(new_item_loc)

            db.session.commit()

            hq_text = " (HQ)" if is_hq else ""
            flash(f'Added {quantity} x {item_name}{hq_text} to storage.', 'success')

        except ValueError:
            flash('Invalid quantity entered.', 'error')
        # pylint: disable=broad-exception-caught
        except Exception as e:
            db.session.rollback()
            flash('Error adding item: {type(e).__name__}: {str(e)}', 'error')

        return redirect(url_for('character_detail', char_id=char_id))

    # pylint: disable=unused-variable
    @app.route('/remove_item_from_storage/<int:storage_id>/<int:item_id>', methods=['POST'])
    def remove_item_from_storage(storage_id, item_id):
        """Remove an item (or reduce quantity) from a storage location."""
        try:
            char_id = int(request.form.get('char_id'))

            if not char_id:
                flash('Character ID missing.', 'error')
                return redirect(url_for('characters'))

            # Find the item location entry
            item_loc = ItemLocations.query.filter_by(
                Storage_ID=storage_id,
                Item_ID=item_id
            ).first_or_404()

            # For simplicity, we'll completely remove the entry for now
            # (Later we can add quantity reduction if desired)
            db.session.delete(item_loc)
            db.session.commit()

            flash('Item Removed from storage successfully', 'success')

        # pylint: disable=broad-exception-caught
        except Exception as e:
            db.session.rollback()
            flash(f'Error removing item: {str(e)}', 'error ')

        # Redirect back to the character detail page

        return redirect(url_for('character_detail', char_id=char_id))

    # pylint: disable=unused-variable
    @app.route('/update_item_quantity/<int:storage_id>/<int:item_id>', methods=['POST'])
    def update_item_quantity(storage_id, item_id):
        """Update quantity (Normal and HQ) for an item in storage. """
        char_id = None

        try:
            normal_qty = int(request.form.get('normal_quantity', 0))
            hq_qty = int(request.form.get('hq_quantity', 0))
            char_id = int(request.form.get('char_id'))

            if not char_id:
                flash('Character ID missing.', 'error')
                return redirect(url_for('characters'))

            # Basic validation
            if normal_qty < 0 or hq_qty < 0:
                flash('Quantities cannot be negative.', 'error')
                return redirect(url_for('character_detail', char_id=char_id))

            #Find the specific item in this storage
            item_loc = ItemLocations.query.filter_by(
                Storage_ID=storage_id,
                Item_ID=item_id
            ).first()

            if not item_loc:
                flash('Item not found in this storage.', 'error')
                return redirect(url_for('character_detail', char_id=char_id))

            #update quantities
            item_loc.Quantity = normal_qty
            item_loc.Quantity_HQ = hq_qty

            db.session.commit()
            flash('Item quantities updated successfully.', 'success')

        except ValueError:
            flash('Invalid quantity values entered.', 'error')
        # pylint: disable=broad-exception-caught
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating quantities: {str(e)}', 'error')

        return redirect(url_for('character_detail', char_id=char_id))

    @app.route('/debug_item_loc/<int:storage_id>/<int:item_id>')
    def debug_item_loc(storage_id, item_id):
        """Debug route to see what ItemLocation rows exist"""
        items = ItemLocations.query.filter_by(
            Storage_ID=storage_id,
            Item_ID=item_id
        ).all()

        output = f"<h3>Debug for Storage_ID={storage_id}, Item_ID={item_id}</h3>"
        output += f"<p>Found {len(items)} matching rows:</p><ul>"

        for i, row in enumerate(items):
            output += f"<li>Row {i+1}: Storage_ID={row.Storage_ID}, Item_ID={row.Item_ID},\
                    Quantity={row.Quantity}, Quantity_HQ={row.Quantity_HQ}</li>"

        output += "</ul>"
        return output

    return app



if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
