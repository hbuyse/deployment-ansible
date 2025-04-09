return {
  {
    'echasnovski/mini.hipatterns',
    version = '*', -- Stable only
    config = function()
      local hipatterns = require('mini.hipatterns')
      hipatterns.setup({
        highlighters = {
          -- Highlight standalone 'FIXME', 'HACK', 'TODO', 'NOTE'
          fixme = { pattern = '%f[%w]()FIXME()%f[%W]', group = 'MiniHipatternsFixme' },
          hack = { pattern = '%f[%w]()HACK()%f[%W]', group = 'MiniHipatternsHack' },
          todo = { pattern = '%f[%w]()TODO()%f[%W]', group = 'MiniHipatternsTodo' },
          note = { pattern = '%f[%w]()NOTE()%f[%W]', group = 'MiniHipatternsNote' }, --

          -- Highlight hex color strings (`#rrggbb`) using that color
          hex_color = hipatterns.gen_highlighter.hex_color({ style = 'full' }),

          -- Highlight trailing whitespaces
          word_color = { pattern = '%f[%s]%s*$', group = 'ExtraWhitespace' },
        },
      })
    end,
    init = function()
      vim.api.nvim_set_hl(0, 'ExtraWhitespace', { ctermbg = 108, bg = '#689d6a' })
    end,
  },
}
