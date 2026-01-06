<script>
  export let text = '';
</script>

<span class="group relative inline-flex items-center ml-1">
  <span class="text-gray-400 cursor-help text-xs">&#9432;</span>
  <span class="invisible group-hover:visible absolute z-20 bg-gray-800 text-white text-xs rounded py-2 px-3 -top-2 left-6 w-64 shadow-lg">
    {text}
    <span class="absolute -left-1 top-3 w-2 h-2 bg-gray-800 transform rotate-45"></span>
  </span>
</span>
