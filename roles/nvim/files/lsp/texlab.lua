return {
  cmd = { 'texlab' },
  filetypes = { 'bib', 'plaintex', 'tex' },
  settings = {
    texlab = {
      build = {
        -- Set this property to true if you want to compile the project after saving a file.
        onSave = false,
      },
      chktex = {
        -- Lint using chktex after opening and saving a file.
        onOpenAndSave = true,
        -- Lint using chktex after editing a file
        onEdit = false,
      },
      -- Delay in milliseconds before reporting diagnostics
      diagnosticsDelay = 100,
      -- Defines the maximum amount of characters per line (0 = disable) when formatting BibTeX files
      formatterLineLength = 120,
      latexindent = {
        -- Modifies linebreaks before, during, and at the end of code blocks when formatting with latexindent.
        -- This corresponds to the --modifylinebreaks flag of latexindent
        modifyLineBreaks = true,
      },
    },
  },
}
