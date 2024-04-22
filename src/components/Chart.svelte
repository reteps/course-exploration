<script lang="ts">
    import { scaleTime, scaleLinear, scaleOrdinal, line, extent, max, curveMonotoneX, axisBottom } from "d3";
    import { schemeTableau10 } from 'd3-scale-chromatic';
    import rawData from './ices.json';
    import type { IDataset, DepartmentKeys } from './types.ts'
    const data: IDataset = rawData;
    let fullWidth = 1200;
    let fullHeight = 800;
    const margin = { top: 20, right: 20, bottom: 30, left: 40 };
    const chartWidth = fullWidth - margin.left - margin.right;
    const chartHeight = fullHeight - margin.top - margin.bottom;

    $: hoveredUnit = '';

    // when hoveredUnit changes, console log
    $: if (hoveredUnit) {
      console.log(hoveredUnit);
    }
    // // Add key for "Faculty Sum"
    // for (const [unit, values] of Object.entries(data)) {
      
    //   // reduce dictionary
    //   const keys = Object.keys(values) as DepartmentKeys;
    //   let facultySums = []
    //   // Loop over each year
    //   for (let i = 0; i < values.years.length; i++) {

    //     const facultySum = keys.filter( key => key.indexOf('Faculty') > -1).reduce((acc, key) => {
    //       return acc + (((values[key] || [])[i] || 0) as number);
    //     }, 0);
    //     facultySums.push(facultySum);
    //   }
    //   data[unit]["Faculty Count"] = facultySums;
    // }
  
    let allYears = ([] as Date[]).concat(...Object.values(data).map(d => d.years.map(year => new Date(+year.split("-")[0], 0, 1))));
    let allValues = ([] as (number | null)[]).concat(...Object.values(data).map((d) => {
      return d["Next 20% Faculty"]?.map((value, i) => {
        return (value === null || value === 100) ? null : value
      }) || []
    })).filter(d => d !== null) as number[]
    const yearExtent = extent(allYears) as [Date, Date];
    const valueMax = 50 // max(allValues) as number;

    const xScale = scaleTime().domain(yearExtent).range([0, chartWidth]);
    const yScale = scaleLinear().domain([0, valueMax]).range([chartHeight, 0]);


    type Datapoint = { value: number, year: number };
    // Line generator
    const drawLine = line<Datapoint>()
        .x((data: Datapoint) => {
          const date = new Date(data.year, 0, 1);
          return xScale(date)
        })
        .y((data: Datapoint) => {
          return yScale(data.value)
        })
        .curve(curveMonotoneX);
        const colorScale = scaleOrdinal(schemeTableau10);

    let formattedValues = Object.entries(data).map(([unit, values]) => {
      const mappedValues = (values["Next 20% Faculty"]?.map((value, i) => ({
          value: value === null ? null : value,
          year: +values.years[i].split("-")[0]
        })) || []).filter( d => d.value !== null) as Datapoint[]
      
      // Ensure that there is content for some year > 2019
      let filteredValues = mappedValues.some( d => d.year > 2019 && d.value !== null) ? mappedValues : []
      
      // Filter out years with <10% ICES response rate
      filteredValues = filteredValues.filter( (d, i) => {
        return (values["% Sections using ICES"]?.[i] || 0) > 10
      })


      return {
        unit,
        values: filteredValues
      }
    })

    // Only keep engineering and computer science
    formattedValues = formattedValues.filter( d => d.unit.toLowerCase().indexOf("eng") > -1 || d.unit === "Computer Science")

    console.log(formattedValues[0].values)

    const xTicks = xScale.ticks().map( d => {
      return {
        value: d.getFullYear(),
        x: xScale(d),
      }
    }
    )

    const yTicks = yScale.ticks().map( d => {
      return {
        value: d,
        y: yScale(d),
      }
    })

</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<div
>
  <h1>Next 20% Faculty</h1>
  <p>Hover over the lines to see the values</p>
</div>

<svg width="{fullWidth}" height="{fullHeight}">
  <g transform="translate({margin.left}, {margin.top})"
  >
    {#each formattedValues as {unit, values}, i}
      <path d={drawLine(values)} fill="none" stroke={colorScale(unit)} stroke-width={unit === hoveredUnit ? '8' : '4'} 
        on:mouseover={() => { hoveredUnit = unit } }
        on:mouseout={() => hoveredUnit = ''}
        pointer-events="stroke"
        role="button"
        tabindex="{-i}"
        on:focus={() => hoveredUnit = unit}
        on:blur={() => hoveredUnit = ''}
      />
    {/each}
    <line x1="0" y1="{chartHeight}" x2="{chartWidth}" y2="{chartHeight}" stroke="black" />
    {#each xTicks as { value, x } }
      <g transform="translate({x}, {chartHeight})">
        <line y2="6" stroke="black" />
        <text dy=".71em" x="0" y="10" text-anchor="middle">{value}</text>
      </g>
    {/each}
    <line x1="0" y1="0" x2="0" y2="{chartHeight}" stroke="black" />
    {#each yTicks as { value, y } }
      <g transform="translate(0, {y})">
        <line x2="-6" stroke="black" />
        <text dy=".32em" x="-9" y="0" text-anchor="end">{value}</text>
      </g>
    {/each}
  </g>
</svg>