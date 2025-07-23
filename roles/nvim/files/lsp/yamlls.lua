--- @class vim.lsp.Config
return {
  cmd = { 'yaml-language-server', '--stdio' },
  filetypes = { 'yaml', 'yaml.docker-compose', 'yaml.gitlab' },
  settings = {
    yaml = {
      -- https://github.com/redhat-developer/vscode-redhat-telemetry#how-to-disable-telemetry-reporting
      redhat = { telemetry = { enabled = false } },
      validate = true,
      schemaStore = {
        enable = true,
        url = 'https://www.schemastore.org/api/json/catalog.json',
      },
      format = { enabled = false },
      schemas = {
        ['http://json.schemastore.org/prettierrc'] = '.prettierrc.{yml,yaml}',
      },
    },
  },
}
