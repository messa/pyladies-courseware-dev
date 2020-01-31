import React from 'react'
import { Button } from 'semantic-ui-react'
import CodeEditor from './CodeEditor'

const defaultCode = ''

export default class TaskSubmission extends React.Component {

  constructor(props) {
    super(props)
    this.state = {
      code: props.code || defaultCode
    }
  }

  handleCodeChange = (newValue) => {
    if (!this.props.loading) {
      this.setState({ code: newValue })
    }
  }

  handleSubmitClick = (event) => {
    event.preventDefault()
    const { code } = this.state
    this.props.onSubmit({ code })
  }

  handleCancelClick = (event) => {
    event.preventDefault()
    this.props.onCancel()
  }

  render() {
    const { loading } = this.props
    const { code } = this.state
    return (
      <form className='TaskSubmitForm' onSubmit={this.handleSubmitClick}>
        <CodeEditor
          value={code}
          onValueChange={this.handleCodeChange}
          disabled={loading}
        />
        <div style={{ marginTop: 10 }}>
          <label>
            Pokud chcete, můžete nahrát soubor:{' '}
          </label>
          <input
            type='file'
            multiple
            />
        </div>
        <div style={{ marginTop: 10 }}>
          <Button
            type='submit'
            size='small'
            primary
            icon='send'
            content='Odeslat'
            onClick={this.handleSubmitClick}
            loading={loading}
            disabled={loading}
          />
          <Button
            size='small'
            color='red'
            icon='cancel'
            content='Zrušit'
            onClick={this.handleCancelClick}
            loading={loading}
            disabled={loading}
          />
        </div>
      </form>
    )
  }

}
