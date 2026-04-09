-- Diagnostic config
local function suffix(d)
  return string.format(' [%s]', d.code and d.code or 'Unknown')
end

local function on_jump(diagnostic, bufnr)
  if not diagnostic then
    return
  end
  vim.diagnostic.show(
    diagnostic.namespace,
    bufnr,
    { diagnostic },
    { virtual_lines = { current_line = true }, virtual_text = false }
  )
end

vim.diagnostic.config({
  float = {
    source = false,
    border = 'double',
    severity_sort = true,
    suffix = suffix,
  },
  virtual_text = {
    source = true,
    prefix = '●',
    spacing = 4,
    suffix = suffix,
    virt_text_pos = 'eol',
    hl_mode = 'combine',
  },
  virtual_lines = false,
  signs = {
    text = {
      [vim.diagnostic.severity.ERROR] = ' ',
      [vim.diagnostic.severity.WARN] = ' ',
      [vim.diagnostic.severity.INFO] = ' ',
      [vim.diagnostic.severity.HINT] = ' ',
    },
  },
  underline = true,
  severity_sort = true,
  jump = {
    on_jump = on_jump,
  },
  update_in_insert = false,
})

local border = { '╭', '─', '╮', '│', '╯', '─', '╰', '│' }
local open_floating_preview = vim.lsp.util.open_floating_preview
---@diagnostic disable-next-line: duplicate-set-field
vim.lsp.util.open_floating_preview = function(contents, syntax, options, ...)
  options = options or {}
  options.border = options.border or border
  return open_floating_preview(contents, syntax, options, ...)
end

--- Setup mapping when attaching LSP server
---@param client table LSP client
---@param bufnr integer Buffer number
local function lsp_keymaps(_, bufnr)
  --- Wrapper function to set keymap
  ---@param m string|table The modes
  ---@param lhs string Keymap
  ---@param rhs string|function Command called when pressing keymap
  ---@param desc string Keymap description
  local kmap = function(m, lhs, rhs, desc)
    local opts = { remap = false, silent = true, buffer = bufnr, desc = desc }
    vim.keymap.set(m, lhs, rhs, opts)
  end

  -- Diagnostics keymaps
  kmap('n', '<leader>dn', function()
    vim.diagnostic.jump({ count = 1 })
  end, '[D]iagnostic [N]ext')
  kmap('n', '<leader>dp', function()
    vim.diagnostic.jump({ count = -1 })
  end, '[D]iagnostic [P]revious')
  kmap('n', '<leader>dl', vim.diagnostic.open_float, '[D]iagnostics In [L]ine')
  -- Toggle diagnostics (global)
  kmap('n', '<leader>de', function()
    vim.diagnostic.enable(not vim.diagnostic.is_enabled())
  end, '[D]iagnostic [E]nable')

  -- LSP keymaps
  kmap('n', 'K', vim.lsp.buf.hover, 'Hover Documentation')
  kmap('n', '<c-k>', vim.lsp.buf.signature_help, 'Signature Documentation')
  kmap('n', '<leader>ca', vim.lsp.buf.code_action, '[C]ode [A]ction')
  kmap('n', '<leader>rn', vim.lsp.buf.rename, '[R]e[N]ame')
end

local function lsp_document_highlight(bufnr)
  local gid = vim.api.nvim_create_augroup('LSPDocumentHighlight', { clear = false })
  vim.api.nvim_clear_autocmds({
    group = gid,
    buffer = bufnr,
  })

  vim.api.nvim_create_autocmd({ 'CursorHold', 'InsertLeave' }, {
    group = gid,
    desc = 'Highlight document using LSP server capabilities',
    buffer = bufnr,
    callback = vim.lsp.buf.document_highlight,
  })
  vim.api.nvim_create_autocmd({ 'CursorMoved', 'InsertEnter', 'BufLeave' }, {
    group = gid,
    desc = 'Clear document highlights using LSP server capabilities',
    buffer = bufnr,
    callback = vim.lsp.buf.clear_references,
  })
end

--- Create augroup and autocommands for InlayHints
---@param bufnr integer Buffer number
local function lsp_inlay_hints(bufnr)
  local gid = vim.api.nvim_create_augroup('LSPInlayHints', { clear = false })
  vim.api.nvim_clear_autocmds({
    group = gid,
    buffer = bufnr,
  })

  -- Initial inlay hint display.
  local mode = vim.api.nvim_get_mode().mode
  if mode == 'n' or mode == 'v' then
    vim.lsp.inlay_hint.enable(true, { bufnr = bufnr })
  end

  vim.api.nvim_create_autocmd('InsertEnter', {
    group = gid,
    desc = 'Disable the inlay hints',
    buffer = bufnr,
    callback = function()
      vim.lsp.inlay_hint.enable(false, { bufnr = bufnr })
    end,
  })
  vim.api.nvim_create_autocmd('InsertLeave', {
    group = gid,
    desc = 'Enable the inlay hints',
    buffer = bufnr,
    callback = function()
      vim.lsp.inlay_hint.enable(true, { bufnr = bufnr })
    end,
  })
end

local function on_attach(client, bufnr)
  lsp_keymaps(client, bufnr)

  -- Inlay hints
  if vim.g.inlay_hint_enabled then
    vim.lsp.inlay_hint.enable(true, { bufnr = bufnr })
  end
  -- Toggle (buffer-local)
  vim.keymap.set('n', '\\h', function()
    local is_enabled = vim.lsp.inlay_hint.is_enabled({ bufnr = 0 })
    vim.b.inlay_hint_enabled = not is_enabled
    vim.lsp.inlay_hint.enable(vim.b.inlay_hint_enabled, { bufnr = 0 })

    vim.notify(
      string.format('Inlay hints (buffer-local) is %s', vim.b.inlay_hint_enabled and 'enabled' or 'disabled'),
      vim.log.levels.INFO
    )
  end, {})

  -- Toggle (global)
  vim.keymap.set('n', '\\H', function()
    vim.g.inlay_hint_enabled = not vim.g.inlay_hint_enabled
    vim.lsp.inlay_hint.enable(vim.g.inlay_hint_enabled)
    vim.notify(
      string.format('Inlay hints (global) is %s', vim.g.inlay_hint_enabled and 'enabled' or 'disabled'),
      vim.log.levels.INFO
    )
  end, {})

  -- Document highlight
  if client:supports_method('textDocument/InlayHint') then
    lsp_inlay_hints(bufnr)
  else
    vim.notify('Server not supporting', vim.log.levels.INFO, { title = 'InlayHints' })
  end

  -- Document highlight
  if client:supports_method('textDocument/documentHighlight') then
    lsp_document_highlight(bufnr)
  end

  -- Nvim-navic automatic attachment
  if client.server_capabilities.documentSymbolProvider then
    require('nvim-navic').attach(client, bufnr)
  end
end

vim.lsp.config('*', {
  on_attach = on_attach,
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
  'pyright', -- Python
  'ruff', -- Python
  'cmake', -- CMake
  'cssls', -- CSS
  'rust_analyzer', -- Rust
  'texlab', -- LaTeX
  'ansiblels', -- Ansible
  'composels', -- Docker compose
  'tombi', -- Toml
  'tailwindcss', -- Tailwindcss
  'perlnavigator', -- Perl
})
