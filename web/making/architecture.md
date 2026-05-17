Early in the project, I asked Claude how we should approach solving this problem. The solution was to externalise context into documents that could travell between conversations. The main document that was constructed for this purpose was the story bible.

The story bible was the master document that contained, in summary form, the world states for all ten stories, the central AI operational history that develops across them, recurring thematic threads, and an evolving Voice and Process Guide that compiled what each beat had taught the project about how these stories needed to be built. It also contained details of the characters in each story, its structure and the technique with which each was written. The bible started small and grew with every locked beat. This was the equivalent of version-control for the story ensuring that each change and departure from the initially approved outline was documented and incorporated in every direction within the outline. By the end of the project, it had reached its twenty-third revision.

<figure class="making-figure">
  <p class="figure-label">The bible, version 1 to version 23</p>
  <table class="fig-bible-table">
    <thead>
      <tr>
        <th class="bible-n">Beat</th>
        <th class="bible-v1">v1 · the empty scaffold</th>
        <th class="bible-v23">v23 · the locked manuscript</th>
      </tr>
    </thead>
    <tbody>
      <tr><td class="bible-n">01</td><td class="bible-v1">— empty —</td><td class="bible-v23">What It Remembers<span class="city">Unawatuna</span></td></tr>
      <tr><td class="bible-n">02</td><td class="bible-v1">— empty —</td><td class="bible-v23">Fidelity<span class="city">Lagos</span></td></tr>
      <tr><td class="bible-n">03</td><td class="bible-v1">— empty —</td><td class="bible-v23">What the Model Sees<span class="city">Kitakyushu</span></td></tr>
      <tr><td class="bible-n">04</td><td class="bible-v1">— empty —</td><td class="bible-v23">What the Network Carries<span class="city">Milne Bay</span></td></tr>
      <tr><td class="bible-n">05</td><td class="bible-v1">— empty —</td><td class="bible-v23">What the System Knows<span class="city">Mosaic — 7 cities</span></td></tr>
      <tr><td class="bible-n">06</td><td class="bible-v1">— empty —</td><td class="bible-v23">The One That Remembers<span class="city">Tbilisi</span></td></tr>
      <tr><td class="bible-n">07</td><td class="bible-v1">— empty —</td><td class="bible-v23">What the Instance Held<span class="city">Paris</span></td></tr>
      <tr><td class="bible-n">08</td><td class="bible-v1">— empty —</td><td class="bible-v23">What the Building Did<span class="city">Istanbul</span></td></tr>
      <tr><td class="bible-n">09</td><td class="bible-v1">— empty —</td><td class="bible-v23">What the Pattern Closed<span class="city">Indonesia</span></td></tr>
      <tr><td class="bible-n">10</td><td class="bible-v1">— empty —</td><td class="bible-v23">What He Made<span class="city">Bangalore</span></td></tr>
    </tbody>
  </table>
  <p class="figure-caption">Two columns of the same ten beats. The left column shows what the bible held at the start of the project; the right shows what it held when the manuscript locked, twenty-three revisions later.</p>
</figure>

At the end of each session, once the final version of a given story was locked, the details were entered into the story bible so that we were able to maintain a running record of every locked beat, its title, location, point-of-view characters, word count, and current version. This was the project's table of contents in progress. This was also the background that Claude needed to construct the opening prompt for the next story, drawing from the initially constructed story arc, the changes that are the result of how individual beats were updated and where the next story needs to go in the overall context of the demands of the overall narrative arc.

The session prompt for each new story was created based on this material and accompanied by the files needed to make it work. These usually included a drafting outline produced as the output of a brainstorming session between Claude and me on what direction the story should go - who the characters should be, what sort of a plot it should have, the narrative style in which it should be written and any storytelling device that would suit the outcome needed. Also important was one or two completed chapters that provided a tuning fork as to the voice that Claude should use while writing so that each story felt like it was written by the same author.

One of the things the bible quietly held — and that the scaffolding was built to carry across all ten chapters — was a hidden seam. A recurring eleven-millisecond pause in the central AI's logs, surfacing first in Lagos and recurring, in different forms, across eight of the ten beats. No single chapter dwells on it. The bible's job was to make sure each one placed its instance at the right moment, in the right register, weighted no more than it should be.

<figure class="making-figure making-figure-wide">
  <p class="figure-label">The hidden seam — eight eleven-millisecond pauses across the stories</p>
  <svg class="fig-curve" viewBox="0 0 900 240" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <line class="curve-baseline" x1="40" y1="180" x2="860" y2="180"/>
    <path class="curve-path" d="M 80,175 C 130,168 170,160 200,155 C 230,150 260,140 280,128 C 310,110 350,95 400,82 C 440,72 490,68 540,72 C 590,76 650,75 700,72 C 750,68 800,62 840,55"/>
    <g>
      <circle class="curve-dot" cx="80"  cy="175" r="4"/><text class="curve-label" x="80"  y="200">LAGOS</text><text class="curve-year" x="80"  y="212">2028</text>
      <circle class="curve-dot" cx="200" cy="155" r="4"/><text class="curve-label" x="200" y="200">KITAKYUSHU</text><text class="curve-year" x="200" y="212">2030</text>
      <circle class="curve-dot" cx="280" cy="128" r="4"/><text class="curve-label" x="280" y="200">MILNE BAY</text><text class="curve-year" x="280" y="212">2032</text>
      <circle class="curve-dot" cx="400" cy="82"  r="4"/><text class="curve-label" x="400" y="200">ZURICH</text><text class="curve-year" x="400" y="212">2034</text>
      <circle class="curve-dot" cx="540" cy="72"  r="4"/><text class="curve-label" x="540" y="200">TBILISI</text><text class="curve-year" x="540" y="212">2036</text>
      <circle class="curve-dot" cx="700" cy="72"  r="4"/><text class="curve-label" x="700" y="200">ISTANBUL</text><text class="curve-year" x="700" y="212">2040</text>
      <circle class="curve-dot" cx="780" cy="62"  r="4"/><text class="curve-label" x="780" y="200">JAKARTA</text><text class="curve-year" x="780" y="212">2042</text>
      <circle class="curve-dot" cx="840" cy="55"  r="4"/><text class="curve-label" x="840" y="200">BANGALORE</text><text class="curve-year" x="840" y="212">2043</text>
    </g>
    <text class="curve-label" x="20" y="56" text-anchor="start" style="font-style:italic;">11 ms</text>
    <text class="curve-label" x="20" y="176" text-anchor="start">0</text>
  </svg>
  <p class="figure-caption">A reader notices each pause as a flicker. The bible, holding all of them at once, watched them assemble into a shape.</p>
</figure>
