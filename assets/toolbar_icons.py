
import tkinter as tk
import base64

# Dictionary to store PhotoImage references to avoid garbage collection
icon_cache = {}

def get_icon_data(name):
    """Return PhotoImage for requested icon"""
    # Base64 encoded PNG data for icons
    icons = {
        "open": "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABmJLR0QA/wD/AP+gvaeTAAAAo0lEQVRIie2UMQ6CQBBF38IF6G2MhXfwLNyGA1ByCxtjtPYW3sDEeAcbQkEiZhZmE4LJFjs72Z83f3YyC38NwzTgBmyBxR8aF+AIPIO8CzAHauAEzP7QuAEHoEr+JdAKiCvwAHbA9EeNM3BOjFVqsAPewFmM1QAjoEgM/uIKXEQz6HJWI1EMQjV6AWmNXkBaoxeQ1ugF/EyjF5DW6AX8tUYPeANRHzbWthge+QAAAABJRU5ErkJggg==",
        "save": "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABmJLR0QA/wD/AP+gvaeTAAAAqklEQVRIie2UMQrCQBBF3xoEa0s7D+E5PIunsLCw9AIWXkc8gXgOGy9gZ2cTEGRlJ7uBEFJ4gBSZmf+Yef+zs/BvmAEH4ApcgC2w+EHjGjgBD+AO7IGpGrQBLsASmEQ0n4Az0AA3YK0aVMAduAFVROMMaIFn9/YGmKgGQ3EEap9GLOUCP0QvQY/QC9Bi9AD1GL0CP0QvQY/QCYmL0AmJi9AJiYhwEfABJwTHPRQNZOQAAAABJRU5ErkJggg==",
        "select": "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABmJLR0QA/wD/AP+gvaeTAAAAk0lEQVRIie2TMQ6CQBBF30IF9GpsOITn4CwcwpLSwgt4HvEEwnks7Kw1IcjKTmYTgskWOzuZfTP/706W4N8wTw3sgTtwBjY/aFwBR+DRy1sCc6AGTsDsB40bcADKfn4p0AqIK/AA9sD0R40zcO4Zq9SgAt7AWYzVACOgSAz+4gpcRDPoelYjUQxCNXoBaY1eQFrjV8AH3GstUJ+BYkgAAAAASUVORK5CYII=",
        "balloon": "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABmJLR0QA/wD/AP+gvaeTAAAA1UlEQVRIie2UMQrCQBBF3xoEay/hOTyLp7CwsPQCFl5HPIHkHDZewM7OJiDIyk52A0tIkQcsImb+Y+b9z84G/g0L4ADcgCuwA1Y/aLwBTsATuAMHYKYGbYELsAamEY1n4Ay0wB3YqAY1cAcewDqicQG0wKt7ewvM1IAh9kDj06gF6DF6AXqMXoAeoxegx+gF6DF6AXqMXkBMjF5ATIxeQEyMXkBMjF5ATIxeQEyMgwEzYAlUwLiQsQROQLFcAZPCxhVQToDxFzSugKIAjsAbeP+i8QfUEzc5qHEvjSYAAAAASUVORK5CYII=",
        "pan": "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABmJLR0QA/wD/AP+gvaeTAAAAeklEQVRIie2UMQqAMAxFX0UQXD2Hp/YsHsWlS72Ai+fxBOJ5XLyAczfbQkWK4FIIZAkk/5H/IQn8G2ZpgD1wBy7A5geNK+AIPLJ8CSyAGjgB8x80boADUGb5UqAVEFfgAeyB6Y8aZ+CcGavUoALewFmM1QAjoEgM+AAftSlQ7dk/qhMAAAAASUVORK5CYII=",
        "zoom_in": "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABmJLR0QA/wD/AP+gvaeTAAAAp0lEQVRIie2TMQrCQBBF3xoEay/hOTyLp7CwsPQCFl5HPIHkHDZewM7OJiDIyk52A0tIkQcsImb+Y+b9z84G/g0L4ADcgCuwA1Y/aLwBTsATuAMHYKYGbYELsAamEY1n4Ay0wB3YqAY1cAcewDqicQG0wKt7ewvM1IAh9kDj06gF6DF6AXqMXoAeoxegx+gF6DF6AXqMXkBMjF5ATIxeQEyMXkBMjB+16TVJ+rDWSwAAAABJRU5ErkJggg==",
        "zoom_out": "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABmJLR0QA/wD/AP+gvaeTAAAApElEQVRIie2UMQrCQBBF3xoEay/hOTyLp7CwsPQCFl5HPIHkHDZewM7OJiDIyk52A0tIkQcsImb+Y+b9z84G/g0L4ADcgCuwA1Y/aLwBTsATuAMHYKYGbYELsAamEY1n4Ay0wB3YqAY1cAcewDqicQG0wKt7ewvM1IAh9kDj06gF6DF6AXqMXoAeoxegx+gF6DF6AXqMXkBMjF5ATIxeQEyMH3k4NaB5SJK3AAAAAElFTkSuQmCC",
        "undo": "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABmJLR0QA/wD/AP+gvaeTAAAAp0lEQVRIie2UMQrCQBBF3xoEa0s7D+E5PIunsLCw9AIWXkc8gXgOGy9gZ2cTEGRlJ7uBEFJ4gBSZmf+Yef+zs/BvmAEH4ApcgC2w+EHjGjgBD+AO7IGpGrQBLsASmEQ0n4Az0AA3YK0aVMAduAFVROMMaIFn9/YGmKgGQ3EEap9GLOUCP0QvQY/QC9Bi9AD1GL0CP0QvQY/QCYmL0AmJi9AJiYhwEfABdyTXAztw6PAAAAABJRU5ErkJggg==",
        "redo": "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABmJLR0QA/wD/AP+gvaeTAAAAqElEQVRIie2UMQrCQBBF3xoEa0s7D+E5PIunsLCw9AIWXkc8gXgOGy9gZ2cTEGRlJ7uBEFJ4gBSZmf+Yef+zs/BvmAEH4ApcgC2w+EHjGjgBD+AO7IGpGrQBLsASmEQ0n4Az0AA3YK0aVMAduAFVROMMaIFn9/YGmKgGQ3EEap9GLOUCP0QvQY/QC9Bi9AD1GL0CP0QvQY/QCYmL0AmJi9AJiYhwEfABfhTXAG/oZKwAAAAASUVORK5CYII="
    }
    
    # Check if the icon is already cached
    if name in icon_cache:
        return icon_cache[name]
    
    # Get base64 data for the icon
    icon_data = icons.get(name, "").strip()
    if not icon_data:
        print(f"Icon not found: {name}")
        return None

    try:
        # Create a PhotoImage from base64 data
        icon = tk.PhotoImage(data=icon_data)
        icon_cache[name] = icon  # Cache the icon to prevent garbage collection
        return icon
    except Exception as e:
        print(f"Error loading icon {name}: {str(e)}")
        return None

    """ try:
        # Get base64 data and strip whitespace
        icon_data = icons.get(name, "").strip()
        if icon_data:
            # Create a simple default icon in case conversion fails
            default_icon = tk.PhotoImage(width=24, height=24)
            
            try:
                # Try to create the icon from base64 data
                photo = tk.PhotoImage(data=icon_data)
                return photo
            except Exception as e:
                print(f"Error loading icon {name}: {str(e)}")
                return default_icon
        return None
    except Exception as e:
        print(f"Error in get_icon_data for {name}: {str(e)}")
        return None """
