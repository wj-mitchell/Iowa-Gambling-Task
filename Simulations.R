# Setting a seed for replicability
set.seed(123)

# Load necessary library
library(dplyr)

# Creating the probabilities
decks <- data.frame(
  A_rewards = c(rep(100, 50), rep(50, 50)),
  A_penalties = c(rep(0, 90), rep(-250, 10)),
  B_rewards = c(rep(100, 50), rep(50, 50)),
  B_penalties = c(rep(0, 90), rep(-1250, 10)),
  C_rewards = c(rep(50, 100)),
  C_penalties = c(rep(0, 90), rep(-50, 10)),
  D_rewards = c(rep(50, 100)),
  D_penalties = c(rep(0, 90), rep(-250, 10))
)

# Function to simulate the Iowa Gambling Task
simulate_IGT <- function(data, trials = 100, limit = 40, dynamic = TRUE, learning_curve = 0.000125) {
  
  # Initialize counts for each deck
  deck_counts <- c(A = 0, B = 0, C = 0, D = 0)
  
  # Initialize net total
  net_total <- 0
  
  # Defining probabilities
  probs <- rep(1/length(deck_counts), length(deck_counts))
  
  # Perform 100 trials
  for (i in 1:trials) {
    
    # Randomly select a deck, ensuring no more than 40 selections from any deck
    available_decks <- names(deck_counts[deck_counts < limit])
    available_probs <- probs[which(deck_counts < limit)]
    selected_deck <- sample(available_decks, size = 1, prob = available_probs)
    
    # Identifying the reward and loss index
    reward_index <- paste0("^", selected_deck, "_rewards") %>% grep(., names(data))
    penalty_index <- paste0("^", selected_deck, "_penalties") %>% grep(., names(data))
    
    # Sample a net reward from the selected deck
    net_reward <- sample(data[,reward_index], size = 1) + sample(data[,penalty_index], size = 1)
    
    # Update net total
    net_total <- net_total + net_reward
    
    # Update the count for the selected deck
    deck_counts[selected_deck] <- deck_counts[selected_deck] + 1
    
    # If dynamic is true
    if (dynamic == TRUE){
      
      # Having a positive net_total will increase the likelihood of selecting that deck again, much as it might in real life
      probs[which(names(deck_counts) == selected_deck)] <- probs[which(names(deck_counts) == selected_deck)] + net_total * learning_curve
      
      # If any of the probabilites now have a negative value
      if (any(probs <= 0)){
        probs <- probs + (1 + -(probs[probs <= 0]))
      }
      
      # Rebalance all of the probabilities 
      probs[which(deck_counts < limit)] <- probs[which(deck_counts < limit)]/sum(probs[which(deck_counts < limit)])
    }
  }
  
  return(net_total)
}

# Running the simulation n times
payout <- replicate(20000, simulate_IGT(data = decks))

# Examining simulation statistics
median(payout)
sd(payout)
hist(payout, 
     main = "Distribution of Possible Payouts in IGT\n(n = 20000)",
     xlab = "Total Net Outcome",
     breaks = 11)

# Function to sample 100 values and calculate their sum
net_sampling <- function(win_data, loss_data, n){ 
  
           rewards <- win_data %>%
                      sample(., n, replace = TRUE) %>%
                      sum()
           losses <- loss_data %>%
                     sample(., n, replace = TRUE) %>%
                     sum()
  return(rewards + losses)
}

# Examining the outcomes if one were to selected the same deck for all trials
hist(replicate(5000, net_sampling(deck_A$rewards, decks$penalties, 100)))
hist(replicate(5000, net_sampling(decks$rewards, decks$penalties, 100)))
hist(replicate(5000, net_sampling(decks$rewards, decks$penalties, 100)))
hist(replicate(5000, net_sampling(decks$rewards, decks$penalties, 100)))
