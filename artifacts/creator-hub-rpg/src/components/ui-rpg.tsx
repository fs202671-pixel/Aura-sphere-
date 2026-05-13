import { cn } from "@/lib/utils";
import { ItemRarity, ItemType, Item } from "@workspace/api-client-react";
import { Link } from "wouter";

export function RarityBadge({ rarity, className }: { rarity: string; className?: string }) {
  return (
    <span
      className={cn(
        "px-2 py-0.5 text-[10px] uppercase tracking-wider font-bold rounded-sm border",
        rarity === "Common" && "bg-gray-500/20 text-gray-400 border-gray-500/30",
        rarity === "Rare" && "bg-blue-500/20 text-blue-400 border-blue-500/30",
        rarity === "Epic" && "bg-purple-500/20 text-purple-400 border-purple-500/30",
        rarity === "Legendary" && "bg-amber-500/20 text-amber-400 border-amber-500/30 legendary-shimmer text-shadow-sm",
        className
      )}
    >
      {rarity}
    </span>
  );
}

export function TypeBadge({ type, className }: { type: string; className?: string }) {
  return (
    <span
      className={cn(
        "px-2 py-0.5 text-[10px] uppercase tracking-wider font-bold rounded-sm border bg-card border-border text-muted-foreground",
        className
      )}
    >
      {type}
    </span>
  );
}

export function ItemCard({ item, onClick }: { item: Item; onClick?: () => void }) {
  const content = (
    <div
      className={cn(
        "relative p-4 rounded-md bg-card border transition-all duration-300 item-card-hover group cursor-pointer flex flex-col h-48",
        `rarity-${item.rarity}`,
        item.rarity === "Common" && "border-gray-500/30",
        item.rarity === "Rare" && "border-blue-500/50 shadow-[0_0_15px_rgba(59,130,246,0.1)] hover:shadow-[0_0_20px_rgba(59,130,246,0.3)]",
        item.rarity === "Epic" && "border-purple-500/50 shadow-[0_0_20px_rgba(168,85,247,0.15)] hover:shadow-[0_0_30px_rgba(168,85,247,0.4)]",
        item.rarity === "Legendary" && "border-amber-500/60 shadow-[0_0_30px_rgba(245,158,11,0.2)] hover:shadow-[0_0_40px_rgba(245,158,11,0.5)]"
      )}
      onClick={onClick}
    >
      {item.rarity === "Legendary" && (
        <div className="absolute inset-0 rounded-md legendary-shimmer pointer-events-none opacity-50" />
      )}
      
      <div className="relative z-10 flex justify-between items-start mb-4">
        <TypeBadge type={item.type} />
        <RarityBadge rarity={item.rarity} />
      </div>
      
      <div className="relative z-10 flex-1">
        <h3 className="font-bold text-lg text-foreground group-hover:text-primary transition-colors truncate">
          {item.name}
        </h3>
        {item.description && (
          <p className="text-xs text-muted-foreground mt-2 line-clamp-3 leading-relaxed">
            {item.description}
          </p>
        )}
      </div>
      
      <div className="relative z-10 flex items-center justify-between mt-4 pt-3 border-t border-border/50">
        <span className="text-[10px] text-muted-foreground font-mono">
          ID: {item.id.toString().padStart(4, "0")}
        </span>
        <span className="text-[10px] text-muted-foreground font-mono">
          {new Date(item.createdAt).toLocaleDateString()}
        </span>
      </div>
    </div>
  );

  if (onClick) return content;
  return <Link href={`/items/${item.id}`}>{content}</Link>;
}
