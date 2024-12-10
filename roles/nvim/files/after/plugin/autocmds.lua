-- Autojump to last known position in the file
local autojump_gid = vim.api.nvim_create_augroup('AutoJump', {})
vim.api.nvim_create_autocmd('BufReadPost', {
  group = autojump_gid,
  desc = 'Autojump to last known position in the file',
  pattern = '*',
  callback = function(_)
    local last_pos = vim.fn.line('\'"')
    local end_pos = vim.fn.line('$')
    if 0 < last_pos and last_pos <= end_pos then
      vim.fn.execute('normal! g\'"')
    end
  end,
})

-- Add folding capacity only if nvim-treesitter parser exists
vim.api.nvim_create_autocmd('FileType', {
  callback = function()
    if not require('nvim-treesitter.parsers').has_parser() then
      return
    end

    vim.opt.foldmethod = 'expr'
    vim.opt.foldexpr = 'nvim_treesitter#foldexpr()'
    vim.opt.foldenable = true
    vim.opt.foldlevel = 3
  end,
})

-- vim: set ts=2 sw=2 tw=0 et ft=lua :
