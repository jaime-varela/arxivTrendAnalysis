import React, { Component } from 'react';
import Table from 'react-bootstrap/Table'


const tableOrderArray = ["abstractBigrams","abstractTrigrams","titleBigrams","titleTrigrams"];

const tableHeaders = {
    abstractBigrams : ["Abstract Bigrams" , "Count"],
    abstractTrigrams : ["Abstract Trigrams" , "Count"],
    titleBigrams : ["Title Bigrams" , "Count"],
    titleTrigrams : ["Title Trigrams" , "Count"],
}


const classificationSiteToStringMap = {'econ':"economics",'math':"mathematics",'cs':"computer_science",
                                        'eess':"eess",'q-bio':"q_biology",'q-fin':"q_finance",'stat':"statistics"}
// should be a class function but I'm lazy
function getLinkFromEntry(site,entry,tableName) {
    const urlPreamble = "https://arxiv.org/search/advanced?advanced=1&terms-0-operator=AND&terms-0-term="
    const includeCross = "&classification-include_cross_list=include&"
    const urlTail = "&date-date_type=submitted_date&abstracts=show&size=50&order=-announced_date_first"
    var term = entry.slice(0,-1).join("+")
    var fieldName = (tableName === "abstractBigrams" || tableName === "abstractBigrams")? "abstract" : "title"
    var classification = ""
    if(site.includes("physics")){
        classification += "classification-physics=y&classification-physics_archives="
        var indexOfSpace = site.indexOf(" ")
        var classVal = site.substring(indexOfSpace+1)
        classification+= classVal
    } else {
        classification += "classification-"+classificationSiteToStringMap[site] + "=y"
    }
    const today = new Date();
    var currentYear = today.getFullYear()  // returns the current year
    var currentMonth = today.getMonth() + 1;

    var lastMonth = (currentMonth != 1)? currentMonth -1 : 12
    currentYear = (currentMonth != 1)? currentYear : currentYear -1
    var lastDay = new Date(currentYear, lastMonth, 0);
    var firstDay = new Date(currentYear, lastMonth-1, 1);

    const offsetLD = lastDay.getTimezoneOffset()
    const offsetFD= firstDay.getTimezoneOffset()
    lastDay = new Date(lastDay.getTime() - (offsetLD*60*1000))
    var lastDayString =  lastDay.toISOString().split('T')[0]
    firstDay = new Date(firstDay.getTime() - (offsetFD*60*1000))
    var firstDayString = firstDay.toISOString().split('T')[0]

    var dateString = "date-year=&date-filter_by=date_range&date-from_date=" + firstDayString + "&date-to_date=" + lastDayString


    return urlPreamble + term + "&terms-0-field=" + fieldName + "&" + classification + includeCross + dateString
    + urlTail
}

class NgramTables extends Component {
    render() {
        return (
            <div>
                {tableOrderArray.map(tableName => {
                    return (
                        <div className="tableDiv">
                        <Table striped bordered hover >
                            <thead>
                                <tr>
                                    {tableHeaders[tableName].map(header => {return <th>{header}</th>})}
                                </tr>
                              </thead>
                              <tbody>
                              {this.props.ngramData[tableName].map(entry => {
                                return(<tr>
                                    <td><a href={getLinkFromEntry(this.props.site,entry,tableName)} target="_blank" rel="noopener noreferrer">{entry.slice(0,-1).join(" ")}</a></td>
                                    <td>{entry[entry.length -1]}</td>
                                </tr>)
                              })}
                              </tbody>
                        </Table>
                        <br></br>
                        </div>
                    )
                })}
            </div>
        );
}
}

export default NgramTables;