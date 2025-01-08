class SafeDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Escape any format string placeholders in values
        for key, value in self.items():
            if isinstance(value, str):
                # Double up curly braces to escape them
                self[key] = value.replace('{', '{{').replace('}', '}}')
    
    def __missing__(self, key):
        return '{' + key + '}'
