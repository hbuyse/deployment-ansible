-- Keep in sync with after/plugin/treesitter.lua
local to_install = {
  'arduino',
  'awk',
  'bash',
  'bibtex',
  'c',
  'cmake',
  'comment',
  'cpp',
  'css',
  'devicetree',
  'diff',
  'dockerfile',
  'func',
  'git_config',
  'git_rebase',
  'gitattributes',
  'gitcommit',
  'gitignore',
  'go',
  'html',
  'htmldjango',
  'http',
  'ini',
  'jq',
  'json',
  'json5',
  'latex',
  'llvm',
  'lua',
  'luadoc',
  'luap',
  'luau',
  'make',
  'markdown',
  'markdown_inline',
  'meson',
  'ninja',
  'nix',
  'passwd',
  'perl',
  'po',
  'proto',
  'puppet',
  'python',
  'query',
  'rst',
  'rust',
  'scheme',
  'scss',
  'sql',
  'toml',
  'twig',
  'typescript',
  'vim',
  'vimdoc',
  'yaml',
}

return {
  {
    'nvim-treesitter/nvim-treesitter',
    dependencies = { 'neovim-treesitter/treesitter-parser-registry' },
    lazy = false,
    build = ':TSUpdate',
    config = function(_, _)
      require('nvim-treesitter').install(to_install)
    end,
    init = function(_)
      vim.api.nvim_create_autocmd('FileType', {
        pattern = to_install,
        callback = function()
          vim.treesitter.start() -- highlighting
          vim.wo.foldexpr = 'v:lua.vim.treesitter.foldexpr()' -- folds
          vim.wo.foldmethod = 'expr'
          vim.bo.indentexpr = "v:lua.require'nvim-treesitter'.indentexpr()" -- indentation
        end,
      })
    end,
  },
}
