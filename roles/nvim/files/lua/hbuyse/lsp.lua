-- Use built-in LSP if Neovim > 0.11
if vim.fn.has('nvim-0.11') == 0 then
  return
end

vim.lsp.config('*', {
  -- on_attach = M.on_attach,
  root_markers = {
    '.git',
  },
})
vim.lsp.enable({
  'clangd', -- C / C++
  'jsonls', -- JSON / JSONC
  'yamlls', -- Yaml
  'bashls', -- Shell
  'luals', -- Lua
  'basedpyright', -- Python
  'cmake', -- CMake
  'cssls', -- CSS
  'rust_analyzer', -- Rust
})
