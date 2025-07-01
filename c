{
  "customCommands": [
    {
      "name": "test",
      "prompt": "{{{ input }}}\n\nWrite a comprehensive set of unit tests for the selected code. It should setup, run tests that check for correctness including important edge cases, and teardown. Ensure that the tests are complete and sophisticated. Give the tests just as chat output, don't edit any file.",
      "description": "Write unit tests for highlighted code"
    },
    {
      "name": "explain",
      "prompt": "{{{ input }}}\n\nExplain this code in detail. Break down complex parts, identify patterns and algorithms used, and highlight any potential issues or optimizations.",
      "description": "Explain the highlighted code in detail"
    }
  ],
  "contextProviders": [
    {
      "name": "currentFile",
      "params": {}
    },
    {
      "name": "diff",
      "params": {}
    },
    {
      "name": "terminal",
      "params": {}
    },
    {
      "name": "problems",
      "params": {}
    },
    {
      "name": "folder",
      "params": {}
    },
    {
      "name": "codebase",
      "params": {}
    },
    {
      "name": "url",
      "params": {}
    }
  ],
  "slashCommands": [
    {
      "name": "edit",
      "description": "Edit selected code"
    },
    {
      "name": "comment",
      "description": "Write comments for the selected code"
    },
    {
      "name": "share",
      "description": "Export the current chat session to markdown"
    },
    {
      "name": "cmd",
      "description": "Generate a shell command"
    },
    {
      "name": "commit",
      "description": "Generate a git commit message"
    }
  ],
  "gitCommitPrompt": "Please write a concise and descriptive git commit message based on the following diff. The message should follow conventional commit format (type(scope): description) where scope indicates the affected component/module (e.g. backend, frontend, api, auth, etc). The message should be clear and informative. Here is the diff:\n\"\"\"\\n{{diff}}\\n\"\"\"\\nCommit(Do NOT wrap with extra quotes): ",
  "experimental": {
    "modelContextProtocolServers": [
      {
        "transport": {
          "type": "stdio",
          "command": "uv",
          "args": [
            "--directory",
            "C:\\Projects\\my-mcp-service",
            "run",
            "my_service"
          ]
        }
      }
    ]
  }
}
