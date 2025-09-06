from notion_client import Client
import os
from datetime import datetime
from dotenv import load_dotenv
import json

class SecondBrain:
    def __init__(self):
        load_dotenv()
        self.notion = Client(auth=os.getenv("NOTION_TOKEN"))
        self.database_id = os.getenv("NOTION_DATABASE_ID")

    def create_page(self, title, content, category="Resource", tags=None, status="To Process"):
        """Create a new page in the Second Brain database."""
        properties = {
            "Title": {"title": [{"text": {"content": title}}]},
            "Category": {"select": {"name": category}},
            "Status": {"select": {"name": status}},
            "Created": {"date": {"start": datetime.now().isoformat()}}
        }

        if tags:
            properties["Tags"] = {"multi_select": [{"name": tag} for tag in tags]}

        page_content = [{
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{
                    "text": {"content": content}
                }]
            }
        }]

        try:
            new_page = self.notion.pages.create(
                parent={"database_id": self.database_id},
                properties=properties,
                children=page_content
            )
            return new_page
        except Exception as e:
            print(f"Error creating page: {e}")
            return None

    def get_pages_by_category(self, category):
        """Retrieve pages by category."""
        try:
            response = self.notion.databases.query(
                database_id=self.database_id,
                filter={
                    "property": "Category",
                    "select": {
                        "equals": category
                    }
                }
            )
            return response["results"]
        except Exception as e:
            print(f"Error retrieving pages: {e}")
            return []

    def update_page_status(self, page_id, new_status):
        """Update the status of a page."""
        try:
            self.notion.pages.update(
                page_id=page_id,
                properties={
                    "Status": {"select": {"name": new_status}}
                }
            )
            return True
        except Exception as e:
            print(f"Error updating page status: {e}")
            return False

    def add_note_to_page(self, page_id, note_content):
        """Add a new note block to an existing page."""
        try:
            self.notion.blocks.children.append(
                block_id=page_id,
                children=[{
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{
                            "text": {"content": note_content}
                        }]
                    }
                }]
            )
            return True
        except Exception as e:
            print(f"Error adding note: {e}")
            return False

if __name__ == "__main__":
    # Example usage
    brain = SecondBrain()
    
    # Create a new note
    new_page = brain.create_page(
        title="My First Note",
        content="This is the content of my first note.",
        category="Resource",
        tags=["productivity", "notes"],
        status="To Process"
    )
    
    if new_page:
        print("Page created successfully!")
        # Add additional note
        brain.add_note_to_page(new_page["id"], "Additional thoughts on this topic...") 