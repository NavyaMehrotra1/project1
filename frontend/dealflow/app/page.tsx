import GraphVisualization from "@/components/graph-visualization"

export default function Home() {
  return (
    <main className="min-h-screen bg-background">
      <div className="container mx-auto p-4">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-foreground mb-2">Company Network Graph</h1>
          <p className="text-muted-foreground">Interactive visualization of company relationships and interactions</p>
        </div>
        <GraphVisualization />
      </div>
    </main>
  )
}
