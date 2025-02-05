return {
  {
    'johnfrankmorgan/whitespace.nvim',
    main = 'whitespace-nvim',
    opts = {
      -- `highlight` configures which highlight is used to display trailing whitespace
      highlight = 'ExtraWhitespace',

      -- `ignored_filetypes` configures which filetypes to ignore when displaying trailing whitespace
      ignored_filetypes = { 'TelescopePrompt', 'Trouble', 'help', 'dashboard' },

      -- `ignore_terminal` configures whether to ignore terminal buffers
      ignore_terminal = true,

      -- `return_cursor` configures if cursor should return to previous position after trimming whitespace
      return_cursor = true,
    },
    init = function()
      vim.api.nvim_set_hl(0, 'ExtraWhitespace', {
        ctermbg = 108,
        bg = '#689d6a',
      })
    end,
  },
}
