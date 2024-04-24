<script lang="ts">
    import type { IAudit }  from './types.ts'
    import rawData from './audit.json';
    const data: IAudit = rawData;
    $: selected = ['Root', 'Suboption'];
    $: activeRequirement = 0
    $: activesubreq = 0

    const onClick = (i: number) => {
        activeRequirement = (activeRequirement == i) ? -1 : i;
        activesubreq = -1;
    }
</script>
<div>
    <div class="text-sm breadcrumbs">
        <ul>
            {#each selected as crumb}
                <li>
                    <a href="#">{crumb}</a>
                </li>
            {/each}
        </ul>
    </div>
    {#each data.requirements as requirement, i}
    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <div class="collapse collapse-arrow border border-base-300 bg-base-200" class:collapse-open={(i == activeRequirement)}>
        <div class="collapse-title text-xl font-medium" on:click={() => onClick(i)}>
          {requirement.name}
        </div>
        <div class="collapse-content"> 
            {#each requirement.subreqs as subreq, j}
            <!-- svelte-ignore a11y-no-static-element-interactions -->
            <!-- svelte-ignore a11y-click-events-have-key-events -->
            <div class="collapse collapse-arrow border border-base-300 bg-base-200" class:collapse-open={(j == activesubreq)} on:click={() => activesubreq = (activesubreq == j) ? -1 : j}>
                <div class="collapse-title text-lg font-medium">
                    {subreq.name}
                </div>
                <div class="collapse-content">
                    <div class="stats">

                        <div class="stat">
                            <div class="stat-title">Courses</div>
                            <div class="stat-value">{subreq.needs.courses}</div>
                        </div>
                        <div class="stat">
                            <div class="stat-title">Hours</div>
                            <div class="stat-value">{subreq.needs.hours}</div>
                        </div>
                    </div>
                </div>
            </div>
            {/each}
        </div>
      </div>
    {/each}
</div>