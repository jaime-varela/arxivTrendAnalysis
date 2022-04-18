import React, { Component } from 'react';
import Form from 'react-bootstrap/Form'
import 'bootstrap/dist/css/bootstrap.min.css';
import NgramTables from './components/NgramTables'

function padding(a, b, c, d) {
  return {
    paddingTop: a,
    paddingRight: b ? b : a,
    paddingBottom: c ? c : a,
    paddingLeft: d ? d : (b ? b : a)
  }
}

class App extends Component {
  constructor(props) {
    super(props);

    this.handleChange = this.handleChange.bind(this);
  }

  // local state for this simple app
  state = {
    sites: [],
    currentSite: "",
    currentNgramData : {},
    isSiteSelected : false,
    allTrendData : {},
  };

  async handleChange(ev) {
    let siteSelected = document.getElementById("arxivSiteSelector").value;
    await this.setState({...this.state,currentSite: siteSelected, currentNgramData: this.state.allTrendData[siteSelected]})
    return;    
  }
  
  async componentDidMount() {
    await this.setState({...this.state,sites: Object.keys(window['trendData'])});
    await this.setState({...this.state,allTrendData: window['trendData']});
  }

  render() {
    return (
    <div>
      <div className="titleHeader">
        <h1>Arxiv Bigram and Trigram Last Month's Trends</h1>
      </div>
      <p style={{...padding(10, 20, 10, 5), color: "black"}}>Updated on the evening of the first of every month</p>
      <br></br>
      <div className="selectArxivSite">
      <Form>
        <Form.Group controlId="exampleForm.SelectCustom">
          <Form.Label>Select Arxiv Site: </Form.Label>
            <Form.Control as="select" custom className="selectorArxivSite" onChange={this.handleChange} id="arxivSiteSelector">
            <option value={""}>Select Site</option>
            {this.state.sites.map(site => {return <option value={site}>{site}</option>})}
            </Form.Control>
          </Form.Group>
        </Form>
        </div>
        {this.state.currentSite == ""? <div></div>:<NgramTables site={this.state.currentSite} ngramData={this.state.currentNgramData}></NgramTables>}
    </div>
    );  
  }
}

export default App;
