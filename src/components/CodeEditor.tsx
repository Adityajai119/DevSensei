import React from 'react'
import Editor from '@monaco-editor/react'

interface CodeEditorProps {
  value: string
  onChange: (value: string) => void
  language: string
  height?: string
  readOnly?: boolean
}

const CodeEditor: React.FC<CodeEditorProps> = ({
  value,
  onChange,
  language,
  height = '300px',
  readOnly = false
}) => {
  const handleEditorChange = (value: string | undefined) => {
    onChange(value || '')
  }

  return (
    <div className="border border-secondary-700 rounded-lg overflow-hidden">
      <Editor
        height={height}
        language={language}
        value={value}
        onChange={handleEditorChange}
        theme="vs-dark"
        options={{
          readOnly,
          minimap: { enabled: false },
          fontSize: 14,
          lineNumbers: 'on',
          roundedSelection: false,
          scrollBeyondLastLine: false,
          automaticLayout: true,
          tabSize: 2,
          insertSpaces: true,
          wordWrap: 'on',
          contextmenu: true,
          selectOnLineNumbers: true,
          glyphMargin: false,
          folding: true,
          lineDecorationsWidth: 10,
          lineNumbersMinChars: 3,
          renderLineHighlight: 'line',
          scrollbar: {
            vertical: 'visible',
            horizontal: 'visible',
            useShadows: false,
            verticalHasArrows: false,
            horizontalHasArrows: false,
          },
        }}
      />
    </div>
  )
}

export default CodeEditor