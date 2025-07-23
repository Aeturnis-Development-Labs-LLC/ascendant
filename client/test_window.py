"""Manual test script to visually verify the PyQt window."""

if __name__ == "__main__":
    import sys
    import os
    # Add parent directory to path so imports work
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from client.app import main
    main()