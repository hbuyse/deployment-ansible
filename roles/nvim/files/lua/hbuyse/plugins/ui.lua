return {
  'folke/snacks.nvim',
  priority = 1000,
  lazy = false,
  ---@type snacks.Config
  opts = {
    -- your configuration comes here
    -- or leave it empty to use the default settings
    -- refer to the configuration section below
    bigfile = {
      enabled = true,
      notify = true, -- show notification when big file detected
      size = 1.5 * 1024 * 1024, -- 1.5MB
      line_length = 1000, -- average line length (useful for minified files)
      -- Enable or disable features when big file detected
      ---@param ctx {buf: number, ft:string}
      setup = function(ctx)
        vim.treesitter.stop()
        Snacks.util.wo(0, { foldmethod = 'manual', statuscolumn = '', conceallevel = 0 })
        vim.b.completion = false
        vim.b.minianimate_disable = true
        vim.b.minihipatterns_disable = true
        vim.schedule(function()
          if vim.api.nvim_buf_is_valid(ctx.buf) then
            vim.bo[ctx.buf].syntax = ctx.ft
          end
        end)
      end,
    },
    dashboard = {
      enabled = true,
      sections = {
        { section = 'header' },
        { icon = ' ', title = 'Keymaps', section = 'keys', indent = 2, padding = 1 },
        { icon = ' ', title = 'Recent Files', section = 'recent_files', indent = 2, padding = 1 },
        { icon = ' ', title = 'Projects', section = 'projects', indent = 2, padding = 1 },
        { section = 'startup' },
      },
    },
    explorer = { enabled = true },
    gh = { enabled = false },
    git = { enabled = true },
    input = {
      enabled = true,
      icon = ' ',
      icon_hl = 'SnacksInputIcon',
      icon_pos = 'left',
      prompt_pos = 'title',
      win = { style = 'input' },
      expand = true,
    },
    picker = {
      enabled = true,
      prompt = ' ',
      sources = {},
      focus = 'input',
      show_delay = 5000,
      limit_live = 10000,
      layout = {
        cycle = true,
        --- Use the default layout or vertical if the window is too narrow
        preset = function()
          return vim.o.columns >= 120 and 'default' or 'vertical'
        end,
      },
      ---@class snacks.picker.matcher.Config
      matcher = {
        fuzzy = true, -- use fuzzy matching
        smartcase = true, -- use smartcase
        ignorecase = true, -- use ignorecase
        sort_empty = false, -- sort results when the search string is empty
        filename_bonus = true, -- give bonus for matching file names (last part of the path)
        file_pos = true, -- support patterns like `file:line:col` and `file:line`
        -- the bonusses below, possibly require string concatenation and path normalization,
        -- so this can have a performance impact for large lists and increase memory usage
        cwd_bonus = false, -- give bonus for matching files in the cwd
        frecency = false, -- frecency bonus
        history_bonus = false, -- give more weight to chronological order
      },
      sort = {
        -- default sort is by score, text length and index
        fields = { 'score:desc', '#text', 'idx' },
      },
      ui_select = true, -- replace `vim.ui.select` with the snacks picker
      ---@class snacks.picker.formatters.Config
      formatters = {
        text = {
          ft = nil, ---@type string? filetype for highlighting
        },
        file = {
          filename_first = false, -- display filename before the file path
          --- * left: truncate the beginning of the path
          --- * center: truncate the middle of the path
          --- * right: truncate the end of the path
          ---@type "left"|"center"|"right"
          truncate = 'center',
          min_width = 40, -- minimum length of the truncated path
          filename_only = false, -- only show the filename
          icon_width = 2, -- width of the icon (in characters)
          git_status_hl = true, -- use the git status highlight group for the filename
        },
        selected = {
          show_always = false, -- only show the selected column when there are multiple selections
          unselected = true, -- use the unselected icon for unselected items
        },
        severity = {
          icons = true, -- show severity icons
          level = false, -- show severity level
          ---@type "left"|"right"
          pos = 'left', -- position of the diagnostics
        },
      },
      ---@class snacks.picker.previewers.Config
      previewers = {
        diff = {
          -- fancy: Snacks fancy diff (borders, multi-column line numbers, syntax highlighting)
          -- syntax: Neovim's built-in diff syntax highlighting
          -- terminal: external command (git's pager for git commands, `cmd` for other diffs)
          style = 'fancy', ---@type "fancy"|"syntax"|"terminal"
          cmd = { 'delta' }, -- example for using `delta` as the external diff command
          ---@type vim.wo?|{} window options for the fancy diff preview window
          wo = {
            breakindent = true,
            wrap = true,
            linebreak = true,
            showbreak = '',
          },
        },
        git = {
          args = {}, -- additional arguments passed to the git command. Useful to set pager options using `-c ...`
        },
        file = {
          max_size = 1024 * 1024, -- 1MB
          max_line_length = 500, -- max line length
          ft = nil, ---@type string? filetype for highlighting. Use `nil` for auto detect
        },
        man_pager = nil, ---@type string? MANPAGER env to use for `man` preview
      },
      ---@class snacks.picker.jump.Config
      jump = {
        jumplist = true, -- save the current position in the jumplist
        tagstack = false, -- save the current position in the tagstack
        reuse_win = false, -- reuse an existing window if the buffer is already open
        close = true, -- close the picker when jumping/editing to a location (defaults to true)
        match = false, -- jump to the first match position. (useful for `lines`)
      },
      toggles = {
        follow = 'f',
        hidden = 'h',
        ignored = 'i',
        modified = 'm',
        regex = { icon = 'R', value = false },
      },
      win = {
        -- input window
        input = {
          keys = {
            -- to close the picker on ESC instead of going to normal mode,
            -- add the following keymap to your config
            ['<Esc>'] = 'cancel',
            ['/'] = 'toggle_focus',
            ['<C-Down>'] = { 'history_forward', mode = { 'i', 'n' } },
            ['<C-Up>'] = { 'history_back', mode = { 'i', 'n' } },
            ['<C-c>'] = { 'close', mode = { 'n', 'i' } },
            ['<C-w>'] = { '<c-s-w>', mode = { 'i' }, expr = true, desc = 'delete word' },
            ['<CR>'] = { 'confirm', mode = { 'n', 'i' } },
            ['<Down>'] = { 'list_down', mode = { 'i', 'n' } },
            ['<S-CR>'] = { { 'pick_win', 'jump' }, mode = { 'n', 'i' } },
            ['<S-Tab>'] = { 'select_and_prev', mode = { 'i', 'n' } },
            ['<Tab>'] = { 'select_and_next', mode = { 'i', 'n' } },
            ['<Up>'] = { 'list_up', mode = { 'i', 'n' } },
            ['<a-d>'] = { 'inspect', mode = { 'n', 'i' } },
            ['<a-f>'] = { 'toggle_follow', mode = { 'i', 'n' } },
            ['<a-h>'] = { 'toggle_hidden', mode = { 'i', 'n' } },
            ['<a-i>'] = { 'toggle_ignored', mode = { 'i', 'n' } },
            ['<a-r>'] = { 'toggle_regex', mode = { 'i', 'n' } },
            ['<a-m>'] = { 'toggle_maximize', mode = { 'i', 'n' } },
            ['<a-p>'] = { 'toggle_preview', mode = { 'i', 'n' } },
            ['<a-w>'] = { 'cycle_win', mode = { 'i', 'n' } },
            ['<c-a>'] = { 'select_all', mode = { 'n', 'i' } },
            ['<c-b>'] = { 'preview_scroll_up', mode = { 'i', 'n' } },
            ['<c-d>'] = { 'list_scroll_down', mode = { 'i', 'n' } },
            ['<c-f>'] = { 'preview_scroll_down', mode = { 'i', 'n' } },
            ['<c-g>'] = { 'toggle_live', mode = { 'i', 'n' } },
            ['<c-j>'] = { 'list_down', mode = { 'i', 'n' } },
            ['<c-k>'] = { 'list_up', mode = { 'i', 'n' } },
            ['<c-n>'] = { 'list_down', mode = { 'i', 'n' } },
            ['<c-p>'] = { 'list_up', mode = { 'i', 'n' } },
            ['<c-q>'] = { 'qflist', mode = { 'i', 'n' } },
            ['<c-s>'] = { 'edit_split', mode = { 'i', 'n' } },
            ['<c-t>'] = { 'tab', mode = { 'n', 'i' } },
            ['<c-u>'] = { 'list_scroll_up', mode = { 'i', 'n' } },
            ['<c-v>'] = { 'edit_vsplit', mode = { 'i', 'n' } },
            ['<c-r>#'] = { 'insert_alt', mode = 'i' },
            ['<c-r>%'] = { 'insert_filename', mode = 'i' },
            ['<c-r><c-a>'] = { 'insert_cWORD', mode = 'i' },
            ['<c-r><c-f>'] = { 'insert_file', mode = 'i' },
            ['<c-r><c-l>'] = { 'insert_line', mode = 'i' },
            ['<c-r><c-p>'] = { 'insert_file_full', mode = 'i' },
            ['<c-r><c-w>'] = { 'insert_cword', mode = 'i' },
            ['<c-w>H'] = 'layout_left',
            ['<c-w>J'] = 'layout_bottom',
            ['<c-w>K'] = 'layout_top',
            ['<c-w>L'] = 'layout_right',
            ['?'] = 'toggle_help_input',
            ['G'] = 'list_bottom',
            ['gg'] = 'list_top',
            ['j'] = 'list_down',
            ['k'] = 'list_up',
            ['q'] = 'cancel',
          },
          b = {
            minipairs_disable = true,
          },
        },
        -- result list window
        list = {
          keys = {
            ['/'] = 'toggle_focus',
            ['<2-LeftMouse>'] = 'confirm',
            ['<CR>'] = 'confirm',
            ['<Down>'] = 'list_down',
            ['<Esc>'] = 'cancel',
            ['<C-c>'] = { 'close', mode = { 'n', 'i' } },
            ['<S-CR>'] = { { 'pick_win', 'jump' } },
            ['<S-Tab>'] = { 'select_and_prev', mode = { 'n', 'x' } },
            ['<Tab>'] = { 'select_and_next', mode = { 'n', 'x' } },
            ['<Up>'] = 'list_up',
            ['<a-d>'] = 'inspect',
            ['<a-f>'] = 'toggle_follow',
            ['<a-h>'] = 'toggle_hidden',
            ['<a-i>'] = 'toggle_ignored',
            ['<a-m>'] = 'toggle_maximize',
            ['<a-p>'] = 'toggle_preview',
            ['<a-w>'] = 'cycle_win',
            ['<c-a>'] = 'select_all',
            ['<c-b>'] = 'preview_scroll_up',
            ['<c-d>'] = 'list_scroll_down',
            ['<c-f>'] = 'preview_scroll_down',
            ['<c-j>'] = 'list_down',
            ['<c-k>'] = 'list_up',
            ['<c-n>'] = 'list_down',
            ['<c-p>'] = 'list_up',
            ['<c-q>'] = 'qflist',
            ['<c-g>'] = 'print_path',
            ['<c-s>'] = 'edit_split',
            ['<c-t>'] = 'tab',
            ['<c-u>'] = 'list_scroll_up',
            ['<c-v>'] = 'edit_vsplit',
            ['<c-w>H'] = 'layout_left',
            ['<c-w>J'] = 'layout_bottom',
            ['<c-w>K'] = 'layout_top',
            ['<c-w>L'] = 'layout_right',
            ['?'] = 'toggle_help_list',
            ['G'] = 'list_bottom',
            ['gg'] = 'list_top',
            ['i'] = 'focus_input',
            ['j'] = 'list_down',
            ['k'] = 'list_up',
            ['q'] = 'cancel',
            ['zb'] = 'list_scroll_bottom',
            ['zt'] = 'list_scroll_top',
            ['zz'] = 'list_scroll_center',
          },
          wo = {
            conceallevel = 2,
            concealcursor = 'nvc',
          },
        },
        -- preview window
        preview = {
          keys = {
            ['<Esc>'] = 'cancel',
            ['q'] = 'cancel',
            ['i'] = 'focus_input',
            ['<a-w>'] = 'cycle_win',
          },
        },
      },
      ---@class snacks.picker.icons
      icons = {
        files = {
          enabled = true, -- show file icons
          dir = '󰉋 ',
          dir_open = '󰝰 ',
          file = '󰈔 ',
        },
        keymaps = {
          nowait = '󰓅 ',
        },
        tree = {
          vertical = '│ ',
          middle = '├╴',
          last = '└╴',
        },
        undo = {
          saved = ' ',
        },
        ui = {
          live = '󰐰 ',
          hidden = 'h',
          ignored = 'i',
          follow = 'f',
          selected = '● ',
          unselected = '○ ',
          -- selected = " ",
        },
        git = {
          enabled = true, -- show git icons
          commit = '󰜘 ', -- used by git log
          staged = '●', -- staged changes. always overrides the type icons
          added = '',
          deleted = '',
          ignored = ' ',
          modified = '○',
          renamed = '',
          unmerged = ' ',
          untracked = '?',
        },
        diagnostics = {
          Error = ' ',
          Warn = ' ',
          Hint = ' ',
          Info = ' ',
        },
        lsp = {
          unavailable = '',
          enabled = ' ',
          disabled = ' ',
          attached = '󰖩 ',
        },
        kinds = {
          Array = ' ',
          Boolean = '󰨙 ',
          Class = ' ',
          Color = ' ',
          Control = ' ',
          Collapsed = ' ',
          Constant = '󰏿 ',
          Constructor = ' ',
          Copilot = ' ',
          Enum = ' ',
          EnumMember = ' ',
          Event = ' ',
          Field = ' ',
          File = ' ',
          Folder = ' ',
          Function = '󰊕 ',
          Interface = ' ',
          Key = ' ',
          Keyword = ' ',
          Method = '󰊕 ',
          Module = ' ',
          Namespace = '󰦮 ',
          Null = ' ',
          Number = '󰎠 ',
          Object = ' ',
          Operator = ' ',
          Package = ' ',
          Property = ' ',
          Reference = ' ',
          Snippet = '󱄽 ',
          String = ' ',
          Struct = '󰆼 ',
          Text = ' ',
          TypeParameter = ' ',
          Unit = ' ',
          Unknown = ' ',
          Value = ' ',
          Variable = '󰀫 ',
        },
      },
    },
    notifier = {
      enabled = true,
      timeout = 3000, -- default timeout in ms
      width = { min = 40, max = 0.4 },
      height = { min = 1, max = 0.6 },
      -- editor margin to keep free. tabline and statusline are taken into account automatically
      margin = { top = 0, right = 1, bottom = 0 },
      padding = true, -- add 1 cell of left/right padding to the notification window
      gap = 0, -- gap between notifications
      sort = { 'level', 'added' }, -- sort by level and time
      -- minimum log level to display. TRACE is the lowest
      -- all notifications are stored in history
      level = vim.log.levels.TRACE,
      icons = {
        error = ' ',
        warn = ' ',
        info = ' ',
        debug = ' ',
        trace = ' ',
      },
      keep = function(_)
        return vim.fn.getcmdpos() > 0
      end,
      ---@type snacks.notifier.style
      style = 'compact',
      top_down = true, -- place notifications from top to bottom
      date_format = '%R', -- time format for notifications
      -- format for footer when more lines are available
      -- `%d` is replaced with the number of lines.
      -- only works for styles with a border
      ---@type string|boolean
      more_format = ' ↓ %d lines ',
      refresh = 50, -- refresh at most every 50ms
    },
    quickfile = { enabled = true },
    scroll = { enabled = true },
    statuscolumn = { enabled = true },
    words = { enabled = true },
    indent = {
      enable = true,
      indent = {
        priority = 1,
        enabled = true, -- enable indent guides
        char = '¦',
        only_scope = false, -- only show indent guides of the scope
        only_current = false, -- only show indent guides in the current window
        hl = 'SnacksIndent', ---@type string|string[] hl groups for indent guides
        -- can be a list of hl groups to cycle through
        -- hl = {
        --     "SnacksIndent1",
        --     "SnacksIndent2",
        --     "SnacksIndent3",
        --     "SnacksIndent4",
        --     "SnacksIndent5",
        --     "SnacksIndent6",
        --     "SnacksIndent7",
        --     "SnacksIndent8",
        -- },
      },
      -- animate scopes. Enabled by default for Neovim >= 0.10
      -- Works on older versions but has to trigger redraws during animation.
      ---@class snacks.indent.animate: snacks.animate.Config
      ---@field enabled? boolean
      --- * out: animate outwards from the cursor
      --- * up: animate upwards from the cursor
      --- * down: animate downwards from the cursor
      --- * up_down: animate up or down based on the cursor position
      ---@field style? "out"|"up_down"|"down"|"up"
      animate = {
        enabled = vim.fn.has('nvim-0.10') == 1,
        style = 'out',
        easing = 'linear',
        duration = {
          step = 20, -- ms per step
          total = 500, -- maximum duration
        },
      },
      ---@class snacks.indent.Scope.Config: snacks.scope.Config
      scope = {
        enabled = true, -- enable highlighting the current scope
        priority = 200,
        char = '¦',
        underline = false, -- underline the start of the scope
        only_current = false, -- only show scope in the current window
        hl = 'SnacksIndentScope', ---@type string|string[] hl group for scopes
      },
      chunk = {
        -- when enabled, scopes will be rendered as chunks, except for the
        -- top-level scope which will be rendered as a scope.
        enabled = false,
        -- only show chunk scopes in the current window
        only_current = false,
        priority = 200,
        hl = 'SnacksIndentChunk', ---@type string|string[] hl group for chunk scopes
        char = {
          corner_top = '┌',
          corner_bottom = '└',
          -- corner_top = "╭",
          -- corner_bottom = "╰",
          horizontal = '─',
          vertical = '│',
          arrow = '>',
        },
      },
    },

    -- Styles
    styles = {
      blame_line = {
        width = 0.6,
        height = 0.6,
        border = true,
        title = ' Git Blame ',
        title_pos = 'center',
        ft = 'git',
      },

      input = {
        backdrop = false,
        position = 'float',
        border = true,
        title_pos = 'center',
        height = 1,
        width = 60,
        relative = 'editor',
        noautocmd = true,
        row = 2,
        -- relative = "cursor",
        -- row = -3,
        -- col = 0,
        wo = {
          winhighlight = 'NormalFloat:SnacksInputNormal,FloatBorder:SnacksInputBorder,FloatTitle:SnacksInputTitle',
          cursorline = false,
        },
        bo = {
          filetype = 'snacks_input',
          buftype = 'prompt',
        },
        --- buffer local variables
        b = {
          completion = false, -- disable blink completions in input
        },
        keys = {
          n_esc = { '<esc>', { 'cmp_close', 'cancel' }, mode = 'n', expr = true },
          i_esc = { '<esc>', { 'cmp_close', 'stopinsert' }, mode = 'i', expr = true },
          i_cr = { '<cr>', { 'cmp_accept', 'confirm' }, mode = { 'i', 'n' }, expr = true },
          i_tab = { '<tab>', { 'cmp_select_next', 'cmp' }, mode = 'i', expr = true },
          i_ctrl_w = { '<c-w>', '<c-s-w>', mode = 'i', expr = true },
          i_up = { '<up>', { 'hist_up' }, mode = { 'i', 'n' } },
          i_down = { '<down>', { 'hist_down' }, mode = { 'i', 'n' } },
          q = 'cancel',
        },
      },
    },
  },
  keys = {
    -- Top Pickers & Explorer
    {
      '<leader><space>',
      function()
        Snacks.picker.smart()
      end,
      desc = 'Smart Find Files',
    },
    {
      '<leader>/',
      function()
        Snacks.picker.grep()
      end,
      desc = 'Grep',
    },
    {
      '<leader>:',
      function()
        Snacks.picker.command_history()
      end,
      desc = 'Command History',
    },
    {
      '<leader>n',
      function()
        Snacks.picker.notifications()
      end,
      desc = 'Notification History',
    },
    {
      '<leader>e',
      function()
        Snacks.explorer()
      end,
      desc = 'File Explorer',
    },
    -- find
    {
      '<leader>fb',
      function()
        Snacks.picker.buffers()
      end,
      desc = '[f]ind [b]uffers',
    },
    {
      '<leader>fc',
      function()
        Snacks.picker.files({ cwd = vim.fn.stdpath('config') })
      end,
      desc = '[F]ind Neovim [C]onfig File',
    },
    {
      '<leader>fd',
      function()
        Snacks.picker.files({ cwd = os.getenv('HOME') .. '/Programming/deployment-ansible' })
      end,
      desc = '[F]ind [D]otfile',
    },
    {
      '<C-p>',
      function()
        Snacks.picker.smart()
      end,
      desc = 'Smart Find Files',
    },
    {
      '<leader>fg',
      function()
        Snacks.picker.git_files()
      end,
      desc = 'Find Git Files',
    },
    {
      '<leader>fp',
      function()
        Snacks.picker.projects()
      end,
      desc = 'Projects',
    },
    {
      '<leader>fr',
      function()
        Snacks.picker.recent()
      end,
      desc = 'Recent',
    },
    -- git
    {
      '<leader>gb',
      function()
        Snacks.picker.git_branches()
      end,
      desc = 'Git Branches',
    },
    {
      '<leader>gl',
      function()
        Snacks.picker.git_log()
      end,
      desc = 'Git Log',
    },
    {
      '<leader>gL',
      function()
        Snacks.picker.git_log_line()
      end,
      desc = 'Git Log Line',
    },
    {
      '<leader>gs',
      function()
        Snacks.picker.git_status()
      end,
      desc = 'Git Status',
    },
    {
      '<leader>gS',
      function()
        Snacks.picker.git_stash()
      end,
      desc = 'Git Stash',
    },
    {
      '<leader>gd',
      function()
        Snacks.picker.git_diff()
      end,
      desc = 'Git Diff (Hunks)',
    },
    {
      '<leader>gf',
      function()
        Snacks.picker.git_log_file()
      end,
      desc = 'Git Log File',
    },
    -- Grep
    {
      '<leader>sb',
      function()
        Snacks.picker.lines()
      end,
      desc = 'Buffer Lines',
    },
    {
      '<leader>sB',
      function()
        Snacks.picker.grep_buffers()
      end,
      desc = 'Grep Open Buffers',
    },
    {
      '<leader>sg',
      function()
        Snacks.picker.grep()
      end,
      desc = 'Grep',
    },
    {
      '<leader>sw',
      function()
        Snacks.picker.grep_word()
      end,
      desc = '[s]earch for Visual selection or [w]ord', -- codespell:ignore earch
      mode = { 'n', 'x' },
    },
    -- search
    {
      '<leader>s"',
      function()
        Snacks.picker.registers()
      end,
      desc = '[s]earch registers', -- codespell:ignore earch
    },
    {
      '<leader>s/',
      function()
        Snacks.picker.search_history()
      end,
      desc = '[s]earch history', -- codespell:ignore earch
    },
    {
      '<leader>sa',
      function()
        Snacks.picker.autocmds()
      end,
      desc = '[s]earch [a]utocmds', -- codespell:ignore earch
    },
    {
      '<leader>sb',
      function()
        Snacks.picker.lines()
      end,
      desc = '[s]earch [b]buffer Lines', -- codespell:ignore earch
    },
    {
      '<leader>sc',
      function()
        Snacks.picker.command_history()
      end,
      desc = '[s]earch [c]ommand History', -- codespell:ignore earch
    },
    {
      '<leader>sC',
      function()
        Snacks.picker.commands()
      end,
      desc = '[s]earch [C]ommands', -- codespell:ignore earch
    },
    {
      '<leader>sd',
      function()
        Snacks.picker.diagnostics()
      end,
      desc = '[s]earch [d]iagnostics', -- codespell:ignore earch
    },
    {
      '<leader>sD',
      function()
        Snacks.picker.diagnostics_buffer()
      end,
      desc = '[s]earch Buffer [D]iagnostics', -- codespell:ignore earch
    },
    {
      '<leader>sh',
      function()
        Snacks.picker.help()
      end,
      desc = '[s]earch [h]elp pages', -- codespell:ignore earch
    },
    {
      '<leader>sH',
      function()
        Snacks.picker.highlights()
      end,
      desc = '[s]earch [H]ighlights', -- codespell:ignore earch
    },
    {
      '<leader>si',
      function()
        Snacks.picker.icons()
      end,
      desc = '[s]earch [i]cons', -- codespell:ignore earch
    },
    {
      '<leader>sj',
      function()
        Snacks.picker.jumps()
      end,
      desc = '[s]earch [j]umps', -- codespell:ignore earch
    },
    {
      '<leader>sk',
      function()
        Snacks.picker.keymaps()
      end,
      desc = '[s]earch [k]eymaps', -- codespell:ignore earch
    },
    {
      '<leader>sl',
      function()
        Snacks.picker.loclist()
      end,
      desc = '[s]earch [l]ocation List', -- codespell:ignore earch
    },
    {
      '<leader>sm',
      function()
        Snacks.picker.marks()
      end,
      desc = '[s]earch [m]arks', -- codespell:ignore earch
    },
    {
      '<leader>sM',
      function()
        Snacks.picker.man()
      end,
      desc = '[s]earch [M]an Pages', -- codespell:ignore earch
    },
    {
      '<leader>sp',
      function()
        Snacks.picker.lazy()
      end,
      desc = '[s]earch for [p]lugin Spec', -- codespell:ignore earch
    },
    {
      '<leader>sq',
      function()
        Snacks.picker.qflist()
      end,
      desc = '[s]earch [q]uickfix List', -- codespell:ignore earch
    },
    {
      '<leader>sR',
      function()
        Snacks.picker.resume()
      end,
      desc = '[s]earch [R]esume', -- codespell:ignore earch
    },
    {
      '<leader>su',
      function()
        Snacks.picker.undo()
      end,
      desc = '[s]earch [u]ndo History', -- codespell:ignore earch
    },
    -- LSP
    {
      'gd',
      function()
        Snacks.picker.lsp_definitions()
      end,
      desc = '[g]oto [d]efinition',
    },
    {
      'gD',
      function()
        Snacks.picker.lsp_declarations()
      end,
      desc = '[g]oto [D]eclaration',
    },
    {
      'gr',
      function()
        Snacks.picker.lsp_references()
      end,
      nowait = true,
      desc = '[g]oto [r]eferences',
    },
    {
      'gi',
      function()
        Snacks.picker.lsp_implementations()
      end,
      desc = '[g]oto [i]mplementation',
    },
    {
      'gy',
      function()
        Snacks.picker.lsp_type_definitions()
      end,
      desc = '[g]oto [t]ype definition',
    },
    {
      'gai',
      function()
        Snacks.picker.lsp_incoming_calls()
      end,
      desc = '[g]oto c[a]lls [i]ncoming',
    },
    {
      'gao',
      function()
        Snacks.picker.lsp_outgoing_calls()
      end,
      desc = '[g]oto c[a]lls [o]utcoming',
    },
    {
      '<leader>ss',
      function()
        Snacks.picker.lsp_symbols()
      end,
      desc = '[s]earch LSP [s]ymbols', -- codespell:ignore earch
    },
    {
      '<leader>sS',
      function()
        Snacks.picker.lsp_workspace_symbols()
      end,
      desc = '[s]earch LSP workspace [S]ymbols', -- codespell:ignore earch
    },
  },
}
