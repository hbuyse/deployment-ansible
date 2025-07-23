return {
  cmd = { 'vscode-json-language-server', '--stdio' },
  filetypes = { 'json', 'jsonc' },
  root_markers = { '.git/', 'package.json', 'tsconfig.json' },
  init_options = {
    provideFormatter = true,
  },
  settings = {
    json = {
      validate = {
        enable = true,
      },
      schemas = {
        {
          fileMatch = { 'package.json' },
          url = 'https://json.schemastore.org/package.json',
        },
        {
          fileMatch = { '.prettierrc', '.prettierrc.json', 'prettier.config.json' },
          url = 'https://json.schemastore.org/prettierrc.json',
        },
      },
    },
  },
  -- Add custom command to format entire document
  commands = {
    Format = {
      function()
        vim.lsp.buf.format({ range = { { 0, 0 }, { vim.fn.line('$'), 0 } } })
      end,
    },
  },
}
