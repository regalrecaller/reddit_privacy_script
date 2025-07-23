#!/usr/bin/env python3
"""
Reddit Comment Privacy Script
Edits and optionally deletes comments older than a specified threshold
"""

import praw
import time
import sys
from datetime import datetime, timedelta

def create_reddit_instance():
    """Create and return Reddit instance with user credentials"""
    
    # You'll need to create an app at https://www.reddit.com/prefs/apps
    # Select "script" as the app type
    reddit = praw.Reddit(
        client_id="medh9e6bF1N480-jkfFMaw",        # From your app
        client_secret="HjDHfLzggSijeF9Uo98_AAJe3J5KNg", # From your app
        username="cccanterbury",           # Your Reddit username
        password="Keeping this account secure.",           # Your Reddit password
        user_agent="Comment Privacy Script by /u/cccanterbury"
    )
    
    return reddit

def process_comments(reddit, edit_text="[deleted]", delete_after_edit=True, dry_run=False, days_threshold=30):
    """
    Process comments older than the threshold for the authenticated user
    
    Args:
        reddit: PRAW Reddit instance
        edit_text: Text to replace comments with (default: "[deleted]")
        delete_after_edit: Whether to delete after editing (default: True)
        dry_run: If True, only preview what would happen without making changes
        days_threshold: Only process comments older than this many days (default: 30)
    """
    
    # Get the authenticated user
    user = reddit.user.me()
    print(f"Processing comments for user: {user.name}")
    
    # Counter for statistics
    processed = 0
    edited = 0
    deleted = 0
    skipped = 0
    failed = 0
    
    try:
        # Iterate through all comments
        for comment in user.comments.new(limit=None):
            try:
                # Skip if already edited to our text
                if comment.body == edit_text:
                    print(f"Skipping already edited comment: {comment.id}")
                    continue
                
                # Display comment info
                print(f"\nProcessing comment ID: {comment.id}")
                print(f"Subreddit: r/{comment.subreddit}")
                print(f"Original text preview: {comment.body[:50]}...")
                
                # Calculate comment age
                comment_date = datetime.fromtimestamp(comment.created_utc)
                comment_age_days = (datetime.now() - comment_date).days
                print(f"Comment age: {comment_age_days} days")
                
                # Skip if comment is too recent
                if comment_age_days <= days_threshold:
                    print(f"✓ Skipping comment (only {comment_age_days} days old, threshold is {days_threshold})")
                    skipped += 1
                    continue
                
                if not dry_run:
                    # Edit the comment
                    comment.edit(edit_text)
                    print("✓ Comment edited")
                    edited += 1
                    
                    # Wait a moment for Reddit to process the edit
                    time.sleep(1)
                    
                    # Delete if requested
                    if delete_after_edit:
                        comment.delete()
                        print("✓ Comment deleted")
                        deleted += 1
                        
                        # Rate limiting - Reddit has API limits
                        time.sleep(1)
                else:
                    print(f"[DRY RUN] Would edit and {'delete' if delete_after_edit else 'keep'} this comment ({comment_age_days} days old)")
                
                processed += 1
                
                # Progress update every 10 comments
                if processed % 10 == 0:
                    print(f"\n--- Processed {processed} comments so far ---\n")
                    
            except Exception as e:
                print(f"✗ Error processing comment {comment.id}: {str(e)}")
                failed += 1
                # Continue with next comment even if one fails
                continue
    
    except KeyboardInterrupt:
        print("\n\nScript interrupted by user")
    
    # Final statistics
    print(f"\n{'='*50}")
    print(f"Processing complete!")
    print(f"Total comments found: {processed + skipped}")
    print(f"Comments skipped (too recent): {skipped}")
    if not dry_run:
        print(f"Comments edited: {edited}")
        print(f"Comments deleted: {deleted}")
    else:
        print(f"Comments that would be processed: {processed}")
    print(f"Failed: {failed}")
    print(f"{'='*50}\n")

def main():
    """Main function to run the script"""
    
    print("Reddit Comment Privacy Script")
    print("="*50)
    
    # Safety confirmation
    print("\nThis script will:")
    print("1. Leave recent comments (30 days or newer) completely untouched")
    print("2. Edit older comments to remove content")
    print("3. Optionally delete the edited older comments")
    print("\nThis action cannot be undone!")
    
    # Get user preferences
    edit_text = input("\nEnter replacement text (default 'F'): ").strip() or "F"
    
    days_input = input("Only process comments older than X days (default 30): ").strip()
    days_threshold = int(days_input) if days_input.isdigit() else 30
    
    delete_input = input("Delete comments after editing? (y/n, default y): ").strip().lower()
    delete_after_edit = delete_input != 'n'
    
    dry_run_input = input("Do a dry run first? (y/n, default y): ").strip().lower()
    dry_run = dry_run_input != 'n'
    
    if not dry_run:
        print(f"\nSettings:")
        print(f"- Replacement text: '{edit_text}'")
        print(f"- Process comments older than: {days_threshold} days")
        print(f"- Delete after edit: {delete_after_edit}")
        confirm = input("\nAre you SURE you want to proceed? Type 'YES' to confirm: ").strip()
        if confirm != "YES":
            print("Operation cancelled.")
            sys.exit(0)
    
    try:
        # Create Reddit instance
        print("\nConnecting to Reddit...")
        reddit = create_reddit_instance()
        
        # Verify authentication
        user = reddit.user.me()
        print(f"✓ Successfully authenticated as: {user.name}")
        
        # Process comments
        print(f"\n{'Starting DRY RUN' if dry_run else 'Starting processing'}...")
        process_comments(reddit, edit_text, delete_after_edit, dry_run, days_threshold)
        
        if dry_run:
            print("\nDry run complete. Run again with dry_run = n to actually make changes.")
            
    except Exception as e:
        print(f"\n✗ Fatal error: {str(e)}")
        print("\nMake sure you have:")
        print("1. Installed PRAW: pip install praw")
        print("2. Created a Reddit app at https://www.reddit.com/prefs/apps")
        print("3. Entered your credentials correctly in the script")
        sys.exit(1)

if __name__ == "__main__":
    main()