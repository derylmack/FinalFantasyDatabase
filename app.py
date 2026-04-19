"""
Main Flask applicatoin for FFXIV Database.
Defines the app factory, initializes extentions, and sets up routes.
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from config import Config
from models import db, Server, Character, StorageLocations, Items, ItemLocations

def create_app(config_class=Config):
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
                    flash('Character name is required!' 'error')
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
            except Exception as e:
                flash(f'Error: {str(e)}', 'error')

        # Always redirect back to the characters list        
        return redirect(url_for('characters'))
    
    @app.route('/character/<int:char_id>')
    def character_detail(char_id):
        """Display details for a specific character."""
        character = Character.query.get_or_404(char_id) #Gets the character with the given ID or returns 404
        return render_template('character_detail.html',
                               title=f"{character.Character_Name}'s Details",
                               character=character)                             
    
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

            except Exception as e:
                db.session.rollback()
                flash(f'Error adding storage locations: {str(e)}', 'error')
        return redirect(url_for('character_detail', char_id=char_id))
    
    @app.route('/servers')
    def servers():
        """Display a list of all servers from the database."""
        servers = Server.query.order_by(Server.Server_Name).all() #Gets all servers from the database
        return render_template('servers.html',
                               title='FFXIV Servers',
                               servers=servers)

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

    # pylint: disable=unused_variable
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
    
    # pylint: disable=unused-variable
    @app.route('/add_item_to_storage/<int:storage_id>', methods=['POST'])
    def add_item_to_storage(storage_id):
        """Add an item to a specific storage location."""
        try:
            item_name = request.form.get('item_name').strip()
            quantity = int(request.form.get('quantity', 1))
            is_hq = 'hq' in request.form

            if not item_name:
                flash('Item name is required!', 'error')
                return redirect(url_for('character_detail', char_id=request.args.get('char_id')))
            
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
        
        # Redirect back to the character detail page
        # We need the character_id to redirect properly
        # For now, we'll get it from the storage location
        storage = StorageLocations.query.get(storage_id)
        char_id = storage.Character_ID if storage else 1
        return redirect(url_for('character_detail', char_id=char_id))
    
    # pylint: disable=unused-variable
    @app.route('/remove_item_from_storage/<int:storage_id>/<int:item_id>', methods=['POST'])
    def remove_item_from_storage(storage_id, item_id):
        """Remove an item (or reduce quantity) from a storage location."""
        try:
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
        storage = StorageLocations.query.get(storage_id)
        char_id = storage.Character_ID if storage else 1
        return redirect(url_for('character_detail', char_id=char_id))
    
    # pylint: disable=unused-variable
    @app.route('/update_item_quantity/<int:storage_id>/<int:item_id>', methods=['POST'])
    def update_item_quantity(storage_id, item_id):
        """Update quantity (Normal and HQ) for an item in storage. """
        try:
            normal_qty = int(request.form.get('normal_quantity', 0))
            hq_qty = int(request.form.get('hq_quantity', 0))

            # Basic validation
            if normal_qty < 0 or hq_qty < 0:
                flash('Quantities cannot be negative.', 'error')
                return redirect(url_for('character_detail', char_id=request.args.get('char_id')))
            
            #Find the specific item in this storage
            item_loc = ItemLocations.query.filter_by(
                Storage_ID=storage_id,
                Item_ID=item_id
            ).first()

            if not item_loc:
                flash('Item not found in this storage.', 'error')
                return redirect(url_for('character_detail', char_id=request.args.get('char_id')))

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
            flash(f'Error updateing quantities: {str(e)}', 'error')

        storage = StorageLocations.query.get(storage_id)
        char_id = storage.Character_ID if storage else 1
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
            output += f"<li>Row {i+1}: Storage_ID={row.Storage_ID}, Item_ID={row.Item_ID}, Quantity={row.Quantity}, Quantity_HQ={row.Quantity_HQ}</li>"
    
        output += "</ul>"
        return output
        
    return app



if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
    