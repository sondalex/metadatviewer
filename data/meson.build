desktop_file = i18n.merge_file(
  input: 'io.github.sondalex.MetaDatViewer.desktop.in',
  output: 'io.github.sondalex.MetaDatViewer.desktop',
  type: 'desktop',
  po_dir: '../po',
  install: true,
  install_dir: join_paths(get_option('datadir'), 'applications')
)

desktop_utils = find_program('desktop-file-validate', required: false)
if desktop_utils.found()
  test('Validate desktop file', desktop_utils,
    args: [desktop_file]
  )
endif

mimefile = i18n.merge_file(
  input: 'io.github.sondalex.MetaDatViewer.mimetype.xml.in',
  output: 'io.github.sondalex.MetaDatViewer.application-x-stata-dta.xml',
  po_dir: '../po',
  install: true,
  install_dir: join_paths(get_option('datadir'), 'mime/packages')
)

appstream_file = i18n.merge_file(
  input: 'io.github.sondalex.MetaDatViewer.appdata.xml.in',
  output: 'io.github.sondalex.MetaDatViewer.appdata.xml',
  po_dir: '../po',
  install: true,
  install_dir: join_paths(get_option('datadir'), 'appdata')
)

appstream_util = find_program('appstream-util', required: false)
if appstream_util.found()
  test('Validate appstream file', appstream_util,
    args: ['validate', appstream_file]
  )
endif

install_data('io.github.sondalex.MetaDatViewer.gschema.xml',
  install_dir: join_paths(get_option('datadir'), 'glib-2.0/schemas')
)

compile_schemas = find_program('glib-compile-schemas', required: false)
if compile_schemas.found()
  test('Validate schema file', compile_schemas,
    args: ['--strict', '--dry-run', meson.current_source_dir()]
  )
endif

subdir('icons')
