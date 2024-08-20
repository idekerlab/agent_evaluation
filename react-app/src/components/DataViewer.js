import { AgGridReact } from 'ag-grid-react'
import React, { useState } from 'react'
import FriendlyIFrame from './FriendlyIFrame'
import { fetchIframeSrc } from '../helpers/iFrameHelpers'

const DataViewer = ({data, ...props}) => {
    const [iframeSrc, setIframeSrc] = useState('')

    let colDefs = []
    let rowData = []


    try {
        if (data.length > 0) {
            data.map((row, index) => {
                if (index == 0) {
                    row.map(label => {
                        let newCol = { 
                            field: label, 
                            filter: true,  
                            filterParams: {
                                buttons: ["reset", "apply"],
                                closeOnApply: true
                            },
                            comparator: (valueA, valueB, nodeA, nodeB, isDescending) => {
                                valueA = parseFloat(valueA)
                                valueB = parseFloat(valueB)
                                if (!isNaN(valueA) && !isNaN(valueB)) {
                                    return valueA - valueB
                                } else {
                                    if (isNaN(valueA) && isNaN(valueB)) {
                                        return 0
                                    }
                                    if (!isNaN(valueA))
                                        return isDescending ?  1 : -1
                                    else
                                        return isDescending ?  -1 : 1
                                }
                            }
                        }

                        if (label.includes("HGNC") || (label.includes("Gene") && label.includes("Symbol"))) {
                            newCol["cellRenderer"] = (props) => (
                                    <span 
                                        style={{ color: 'blue', cursor: 'pointer' }}
                                        onClick={() => fetchIframeSrc(props.value, setIframeSrc)}
                                    >
                                        {props.value}
                                    </span>
                                )
                        } 
                        colDefs.push(newCol)
                    })
                } else {
                    let newRow = {}
                    row.map((value, index) => {
                            newRow[`${colDefs[index]["field"]}`] =  value
                    })
                    rowData.push(newRow)
                }
            })
        }
    } catch (error) {
        console.log("Error with dataset");
    }


    return (
        <div>
            { colDefs.length > 0 && rowData.length > 0 ?
                <div className="ag-theme-quartz" style={{ height: 500 }} >
                    <AgGridReact
                        rowData={rowData}
                        columnDefs={colDefs}
                    />
                </div>
                :
                <p style={{color: "red"}}><b>Error displaying table data</b></p>
            }
            {iframeSrc && (
                <FriendlyIFrame iframeSrc={iframeSrc} closeIframe={() => setIframeSrc("")} />
            )}
        </div>
    )
}

export default DataViewer