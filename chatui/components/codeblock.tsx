import React, { PureComponent } from "react";
import PropTypes from "prop-types";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { okaidia as prismStyle } from "react-syntax-highlighter/dist/esm/styles/prism";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCopy, faDownload } from "@fortawesome/free-solid-svg-icons";

class CodeBlock extends PureComponent {
  static propTypes = {
    value: PropTypes.string.isRequired,
    language: PropTypes.string,
  };

  static defaultProps = {
    language: null,
  };

  handleCopy = () => {
    navigator.clipboard.writeText(this.props.value).then(
      () => {
        console.log("Copying to clipboard was successful!");
      },
      (err) => {
        console.error("Could not copy text: ", err);
      }
    );
  };

  handleDownload = () => {
    const blob = new Blob([this.props.value], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "code.txt";
    a.click();
    URL.revokeObjectURL(url);
  };

  render() {
    const { language, value } = this.props;
    return (
      <div style={styles.container}>
        <div style={styles.header}>
          {language && <span style={styles.languageLabel}>{language}</span>}
          <div>
            <button style={styles.iconButton} onClick={this.handleCopy}>
              <FontAwesomeIcon icon={faCopy} />
            </button>
            <button style={styles.iconButton} onClick={this.handleDownload}>
              <FontAwesomeIcon icon={faDownload} />
            </button>
          </div>
        </div>
        <div style={styles.divider}></div>
        <SyntaxHighlighter language={language} style={prismStyle} customStyle={styles.codeBlock}>
          {value}
        </SyntaxHighlighter>
      </div>
    );
  }
}

const styles = {
  container: {
    marginBottom: '1em',
    borderRadius: '0',
    overflow: 'hidden',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#2d2d2d', // Dark background
    padding: '0.3em 0.5em', // Smaller padding for a smaller header
    color: '#fff',
  },
  languageLabel: {
    fontSize: '0.8em',
    fontWeight: 'bold',
  },
  iconButton: {
    backgroundColor: 'transparent',
    border: 'none',
    color: 'white',
    padding: '0.3em',
    cursor: 'pointer',
  },
  divider: {
    height: '1px',
    backgroundColor: '#444', // Faint border color
  },
  codeBlock: {
    margin: 0, // Remove any margin
    borderRadius: '0',
    backgroundColor: '#2d2d2d', // Dark background
  },
};

export default CodeBlock;