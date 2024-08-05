import { AgGridReact } from 'ag-grid-react'

const DataViewer = ({data, ...props}) => {

    let colDefs = []
    let rowData = []


    try {
        if (data.length > 0) {
            data.map((row, index) => {
                if (index == 0) {
                    row.map(label => {
                        colDefs.push({ 
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
                        })
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
        </div>
    )
}

export default DataViewer