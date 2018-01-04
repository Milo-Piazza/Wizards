import argparse
import heapq
import random

class SlideNode:
    def __init__(self, name, value, prev=None, myNext=None):
        self.name = name
        self.value = value
        self.prev = prev
        self.next = myNext
    def setNext(self, tail):
        self.next = tail
        if tail != None:
            tail.prev = self
    def setPrev(self, prev):
        self.prev = prev
        if prev != None:
            prev.next = self
    def removeNode(self):
        tempPrev = self.prev
        tempNext = self.next
        if tempPrev != None:
            self.prev.setNext(tempNext)
        if tempNext != None:
            self.next.setPrev(tempPrev)
        self.prev = None
        self.next = None
    def setValue(self, value):
        self.value = value
    def updateValue(self):
        if self.prev == None:
            self.setValue(self.next.value / 2)
        elif self.next == None:
            self.setValue(self.prev.value * 2)
        else:
            self.setValue((self.prev.value + self.next.value) / 2)

class SlideList:
    def __init__(self, names, interval=1.0):
        self.names = names.copy()
        self.values = dict()
        self.first = SlideNode(names[0], interval)
        prev = self.first
        self.values[names[0]] = self.first
        count = 2.0 * interval
        for name in names[1:]:
            self.values[name] = SlideNode(name, count, prev)
            prev.setNext(self.values[name])
            prev = self.values[name]
            count += interval
    def printNiceOrder(self):
        curr = self.first
        while curr != None:
            print(curr.name, end="")
            curr = curr.next
        print("\n")
    def printOrder(self):
        curr = self.first
        while curr != None:
            print(curr.name)
            print(curr.value)
            curr = curr.next
    def remove(self, name):
        if self.values[name] == self.first:
            self.first = self.first.next
        self.values[name].removeNode()
    def removeNode(self, node):
        if node == self.first:
            self.first = self.first.next
        node.removeNode()
    def getPrev(self, name):
        if self.values[name].prev is None:
            return None
        return self.values[name].prev.name        
    def getNext(self, name):
        if self.values[name].next is None:
            return None
        return self.values[name].next.name
    def slide(self, toMove, after=None):
        nodeToMove = self.values[toMove]
        self.removeNode(nodeToMove)
        if after == None:
            nodeToMove.setNext(self.first)
            nodeToMove.setValue(nodeToMove.value / 2)
            self.first = nodeToMove
        else:
            tempNext = self.values[after].next
            nodeToMove.setNext(tempNext)
            nodeToMove.setPrev(self.values[after])
        nodeToMove.updateValue()
    def checkConstraint(self, constraint):
        v0 = self.values[constraint[0]].value
        v1 = self.values[constraint[1]].value
        vTarget = self.values[constraint[2]].value
        if v0 < vTarget and vTarget < v1 or v1 < vTarget and vTarget < v0:
            return False
        return True
    def asArray(self):
        myList = []
        curr = self.first
        while curr != None:
            myList.append(curr.name)
            curr = curr.next
        return myList
    def totalConstraintsViolated(self, constraints):
        total = 0
        for constraint in constraints:
            if not self.checkConstraint(constraint):
                total += 1
        return total
"""
======================================================================
  Complete the following function.
======================================================================
"""
def alphabetizePair(pair):
    if pair[1] < pair[0]:
        return pair[1] + " " + pair[0]
    return pair[0] + " " + pair[1]
def constraintToString(constraint):
    return constraint[0] + " " + constraint[1] + " " + constraint[2]
def stringToConstraint(string):
    return string.split(" ")

def solve(num_wizards, num_constraints, wizards, constraints):
    """
    Write your algorithm here.
    Input:
        num_wizards: Number of wizards
        num_constraints: Number of constraints
        wizards: An array of wizard names, in no particular order
        constraints: A 2D-array of constraints, 
                     where constraints[0] may take the form ['A', 'B', 'C']i

    Output:
        An array of wizard names in the ordering your algorithm returns
    """
    consPairs = dict()
    for wizard in wizards:
        for otherWizard in wizards:
            if wizard != otherWizard:
                consPairs[alphabetizePair((wizard, otherWizard))] = set()
    for constraint in constraints:
        consPairs[alphabetizePair((constraint[0], constraint[2]))].add(constraintToString(constraint))
        consPairs[alphabetizePair((constraint[1], constraint[2]))].add(constraintToString(constraint))
    wizardList = SlideList(wizards, 50.0)
    violated = dict()
    i = 1
    #target is the maximum number of violated constraints we want in our ordering.
    target = 400
    #we want to break ties based on whether a wizard is the C in each violated constraint (A B C) or not
    tieBreak = 1.0 / (num_wizards + 1)
    #TODO: After finding an order, make random moves and look for a better one?
    while True:
        #find the wizard that violates the most constraints
        print("----- Order", i, "-----\n")
        i += 1
        #wizardList.printNiceOrder()
        for wizard in wizards:
            violated[wizard] = 0
        for constraint in constraints:
            if not wizardList.checkConstraint(constraint):
                violated[constraint[0]] -= 1.0
                violated[constraint[1]] -= 1.0
                violated[constraint[2]] -= 1.0 #+ tieBreak
                #for wizard in constraint:
                    #violated[wizard] -= 1
        #create a priority queue for the wizards sorted by constraints violated
        #note that this is a min queue, which is why we count negative constraints
        wizardQueue = []
        for wizard in wizards:
            heapq.heappush(wizardQueue, (violated[wizard], wizard))
        while True:
            #if we loop too many times, implying an infinite loop
            if i > 20:
                total = wizardList.totalConstraintsViolated(constraints)
                if total <= target:
                    wizardList.printOrder()
                    return wizardList.asArray()
                i = 0
                #make random moves to (hopefully) break the infinite loop
                for _ in range(20):
                    w1 = random.choice(wizards)
                    w2 = random.choice(wizards)
                    if w1 != w2:
                        wizardList.slide(w1, w2)
                break
            originalPositionViolated = sum([0 if wizardList.checkConstraint(constraint) else 1 for constraint in constraints])
            #get the wizard that violates the most constraints
            if len(wizardQueue) == 0:
                #if we look through every wizard and don't find a better position for any of them, we are done
                print("Done! returning order: ", end="")
                #wizardList.printNiceOrder()
                total = wizardList.totalConstraintsViolated(constraints)
                print("Total constraints violated: ", total)
                if total <= target:
                    wizardList.printOrder()
                    return wizardList.asArray()
                i = 0
                #make random moves to (hopefully) find a better ordering
                for _ in range(20):
                    w1 = random.choice(wizards)
                    w2 = random.choice(wizards)
                    if w1 != w2:
                        wizardList.slide(w1, w2)
                break
            naughtyWizardNode = heapq.heappop(wizardQueue)
            #does the wizard not violate any constraints?
            if naughtyWizardNode[0] == 0:
                #if so, we are done
                print("Done! returning order: ", end="")
                wizardList.printNiceOrder()
                total = wizardList.totalConstraintsViolated(constraints)
                print("Total constraints violated: ", total)
                if total <= target:
                    wizardList.printOrder()
                    return wizardList.asArray()
                #make random moves to (hopefully) find a better ordering
                i = 0
                for _ in range(20):
                    w1 = random.choice(wizards)
                    w2 = random.choice(wizards)
                    if w1 != w2:
                        wizardList.slide(w1, w2)
                break
            naughtyWizard = naughtyWizardNode[1]
            originalPosition = wizardList.getPrev(naughtyWizard)
            #print("To move:", naughtyWizard)
            #move wizard to the start
            wizardList.slide(naughtyWizard)
            #check how many constraints are violated
            currentViolated = sum([0 if wizardList.checkConstraint(constraint) else 1 for constraint in constraints])
            minViolated = currentViolated
            #note: slide(wizard, None) moves wizard to the start of the list
            minPositions = [originalPosition]
            #print("Moving:")
            while wizardList.getNext(naughtyWizard) != None:
                #move the wizard ahead one position
                swappedWith = wizardList.getNext(naughtyWizard)
                #print("Swapping with:", swappedWith)
                wizardList.slide(naughtyWizard, swappedWith)
                relevantConstraints = alphabetizePair((naughtyWizard, swappedWith))
                netConstraints = 0
                #count the total number of constraints that change state
                for constraint in consPairs[relevantConstraints]:
                    if wizardList.checkConstraint(stringToConstraint(constraint)):
                        netConstraints -= 1
                    else:
                        netConstraints += 1
                currentViolated += netConstraints
                #does this position violate the fewest constraints so far?
                if currentViolated < minViolated:
                    #if so this is the new best position
                    minPositions = [swappedWith]
                    minViolated = currentViolated
                elif currentViolated == minViolated:
                    #we will add the new position to be randomly selected
                    minPositions.append(swappedWith)
            print("Original constraints:", originalPositionViolated)
            print("New constraints:", minViolated)
            #is the best position better than the original position?
            if minViolated < originalPositionViolated: #changed < to <=
                #if so, we can move the wizard there! (maybe even if not?)
                newPosition = random.choice(minPositions)
                #print("Moving", naughtyWizard, "to", newPosition)
                wizardList.slide(naughtyWizard, newPosition)
                break
            #otherwise: move him back to his original position and try the next one
            #print("Moving the next best wizard:")
            wizardList.slide(naughtyWizard, originalPosition)

"""
======================================================================
   No need to change any code below this line
======================================================================
"""

def read_input(filename):
    with open(filename) as f:
        num_wizards = int(f.readline())
        num_constraints = int(f.readline())
        constraints = []
        wizards = set()
        for _ in range(num_constraints):
            c = f.readline().split()
            constraints.append(c)
            for w in c:
                wizards.add(w)
                
    wizards = list(wizards)
    return num_wizards, num_constraints, wizards, constraints

def write_output(filename, solution):
    with open(filename, "w") as f:
        for wizard in solution:
            f.write("{0} ".format(wizard))

if __name__=="__main__":
    parser = argparse.ArgumentParser(description = "Constraint Solver.")
    parser.add_argument("input_file", type=str, help = "___.in")
    parser.add_argument("output_file", type=str, help = "___.out")
    args = parser.parse_args()
    num_wizards, num_constraints, wizards, constraints = read_input(args.input_file)
    solution = solve(num_wizards, num_constraints, wizards, constraints)
    write_output(args.output_file, solution)
