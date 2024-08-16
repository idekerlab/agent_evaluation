import axios from 'axios'

export const fetchIframeSrc = (geneName, setIframeSrc) => {
    axios.get(`https://rest.uniprot.org/uniprotkb/search?query=(reviewed:true)%20AND%20(gene:${geneName})&format=json`)
        .then(response => {
            const accessId = response.data.results[0].primaryAccession
            // console.log(response.data);
            setIframeSrc(`https://www.uniprot.org/uniprotkb/${accessId}/entry`)
        })
        .catch(error => {
            setIframeSrc("")
            alert(`Sorry we couldn't find any information on the gene: ${geneName}`)
        })
}